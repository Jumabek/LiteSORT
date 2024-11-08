# vim: expandtab:ts=4:sw=4
from __future__ import division, print_function, absolute_import
from fastreid.modeling import build_model
from ultralytics import YOLO

import argparse
import os
import time

import cv2
import numpy as np

from application_util import preprocessing
from application_util import visualization
from deep_sort import nn_matching
from deep_sort.detection import Detection
from deep_sort.tracker import Tracker
from opts import opt


import ntpath
import os
import cv2
from PIL import Image
import torch
from torchvision import transforms
from fastreid.config import get_cfg
from fastreid.utils.checkpoint import Checkpointer


import logging
logging.getLogger().setLevel(logging.ERROR)


def gather_sequence_info(sequence_dir, detection_file):
    """Gather sequence information, such as image filenames, detections,
    groundtruth (if available).

    Parameters
    ----------
    sequence_dir : str
        Path to the MOTChallenge sequence directory.
    detection_file : str
        Path to the detection file.

    Returns
    -------
    Dict
        A dictionary of the following sequence information:

        * sequence_name: Name of the sequence
        * image_filenames: A dictionary that maps frame indices to image
          filenames.
        * detections: A numpy array of detections in MOTChallenge format.
        * groundtruth: A numpy array of ground truth in MOTChallenge format.
        * image_size: Image size (height, width).
        * min_frame_idx: Index of the first frame.
        * max_frame_idx: Index of the last frame.

    """
    image_dir = os.path.join(sequence_dir, "img1")
    image_filenames = {
        int(os.path.splitext(f)[0]): os.path.join(image_dir, f)
        for f in os.listdir(image_dir)}
    groundtruth_file = os.path.join(sequence_dir, "gt/gt.txt")

    detections = None
    # if detection_file is not None:
    #     detections = np.load(detection_file)
    groundtruth = None
    if os.path.exists(groundtruth_file):
        groundtruth = np.loadtxt(groundtruth_file, delimiter=',')

    if len(image_filenames) > 0:
        image = cv2.imread(next(iter(image_filenames.values())),
                           cv2.IMREAD_GRAYSCALE)
        image_size = image.shape
    else:
        image_size = None

    if len(image_filenames) > 0:
        min_frame_idx = min(image_filenames.keys())
        max_frame_idx = max(image_filenames.keys())
    else:
        min_frame_idx = int(detections[:, 0].min())
        max_frame_idx = int(detections[:, 0].max())

    info_filename = os.path.join(sequence_dir, "seqinfo.ini")
    if os.path.exists(info_filename):
        with open(info_filename, "r") as f:
            line_splits = [l.split('=') for l in f.read().splitlines()[1:]]
            info_dict = dict(
                s for s in line_splits if isinstance(s, list) and len(s) == 2)

        update_ms = 1000 / int(info_dict["frameRate"])
    else:
        update_ms = None

    feature_dim = detections.shape[1] - 10 if detections is not None else 0
    seq_info = {
        "sequence_name": os.path.basename(sequence_dir),
        "image_filenames": image_filenames,
        "detections": detections,
        "groundtruth": groundtruth,
        "image_size": image_size,
        "min_frame_idx": min_frame_idx,
        "max_frame_idx": max_frame_idx,
        "feature_dim": feature_dim,
        "update_ms": update_ms
    }
    return seq_info


# This can be defined outside of the main function to avoid redefinition
def get_transform(size=(256, 128)):
    transform = transforms.Compose([
        transforms.Resize(size),
        transforms.ToTensor()
    ])
    return transform


def get_apperance_features(yolo_results, image, reid_model):
    if opt.iou_only:
        # yolo_results[0].appearance_features.cpu().numpy()
        return [None] * len(yolo_results[0].boxes.data)
        # return np.zeros*len(yolo_results[0].boxes.data)

    if opt.LiteSORT:
        return yolo_results[0].appearance_features.cpu().numpy()

    # Convert the image to RGB and then to PIL format only if it's needed
    if opt.BoT:
        img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        transform = get_transform((256, 128))
        boxes = yolo_results[0].boxes.data.cpu().numpy()
        features_list = []

        for box in boxes:
            x1, y1, x2, y2 = box[:4]
            crop = img_pil.crop((x1, y1, x2, y2))
            tensor_crop = transform(crop).unsqueeze(0).cuda()
            feature = reid_model(tensor_crop).detach().cpu().numpy().squeeze()
            features_list.append(feature)

        return features_list  # [N, (2024,)]
    else:  # means deepsort
        boxes = yolo_results[0].boxes.data.cpu().numpy()
        features_list = []

        for box in boxes:
            x1, y1, x2, y2 = map(int, box[:4])

            # Crop using OpenCV
            crop = image[y1:y2, x1:x2]

            # Convert to the RGB format to be consistent with the previous format you used
            crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)

            # Extract features
            feature = reid_model([crop_rgb]).detach().cpu().numpy().squeeze()
            # print(feature.shape)
            features_list.append(feature)
        return features_list  # [N, (1,128)]


def create_detections(seq_dir, frame_index, model, min_height, reid_model=None):
    detection_list = []
    # Get the specific image frame path
    # assuming frame names are like 000001.jpg, 000002.jpg, ...

    ext = '.jpg' if opt.dataset in ['MOT17', 'MOT20'] else '.png'
    img_path = os.path.join(seq_dir, 'img1', f'{frame_index:06}{ext}')
    # print(f"Processing image {img_path}")

    if not os.path.exists(img_path):
        raise ValueError(f"Image path {img_path} doesn't exist.")

    # Load and predict
    image = cv2.imread(img_path)
    # Apply detection for 'person' class
    yolo_results = model.predict(
        image, classes=[0], verbose=False, imgsz=opt.input_resolution, yolosort=opt.LiteSORT, conf=opt.min_confidence)
    appearance_features = get_apperance_features(
        yolo_results, image, reid_model)

    boxes = yolo_results[0].boxes.data.cpu().numpy()

    for box, feature in zip(boxes, appearance_features):
        xmin, ymin, xmax, ymax, conf, _ = box
        x_tl = xmin
        y_tl = ymin
        width = xmax - xmin
        height = ymax - ymin
        bbox = (x_tl, y_tl, width, height)
        if height < min_height:
            continue
        detection = Detection(bbox, conf, feature)

        detection_list.append(detection)

    return detection_list


def create_detections_original(detection_mat, frame_idx, min_height=0):
    "Strongsort original, uses precomputed features and detections"

    """Create detections for given frame index from the raw detection matrix.

    Parameters
    ----------
    detection_mat : ndarray
        Matrix of detections. The first 10 columns of the detection matrix are
        in the standard MOTChallenge detection format. In the remaining columns
        store the feature vector associated with each detection.
    frame_idx : int
        The frame index.
    min_height : Optional[int]
        A minimum detection bounding box height. Detections that are smaller
        than this value are disregarded.

    Returns
    -------
    List[tracker.Detection]
        Returns detection responses at given frame index.

    """
    frame_indices = detection_mat[:, 0].astype(int)
    mask = frame_indices == frame_idx

    detection_list = []
    for row in detection_mat[mask]:
        bbox, confidence, feature = row[2:6], row[6], row[10:]
        if bbox[3] < min_height:
            continue
        detection_list.append(Detection(bbox, confidence, feature))
    return detection_list


def load_reid_model():
    cfg_path = 'checkpoints/FastReID/bagtricks_S50.yml'
    model_weights = 'checkpoints/FastReID/DukeMTMC_BoT-S50.pth'

    cfg = get_cfg()
    cfg.merge_from_file(cfg_path)
    cfg.MODEL.BACKBONE.PRETRAIN = False
    cfg.MODEL.WEIGHTS = model_weights
    model = build_model(cfg)  # Use build_model directly
    model.eval()
    Checkpointer(model).load(cfg.MODEL.WEIGHTS)
    return model


def load_deep_sort_model():
    from deep_apperance import DeepSORTApperanceExtractor
    model = DeepSORTApperanceExtractor(
        "checkpoints/FastReID/deepsort/original_ckpt.t7")

    return model


def run(sequence_dir, detection_file, output_file, min_confidence,
        nms_max_overlap, min_detection_height, max_cosine_distance,
        nn_budget, display):
    """Run multi-target tracker on a particular sequence.

    Parameters
    ----------
    sequence_dir : str
        Path to the MOTChallenge sequence directory.
    detection_file : str
        Path to the detections file.
    output_file : str
        Path to the tracking output file. This file will contain the tracking
        results on completion.
    min_confidence : float
        Detection confidence threshold. Disregard all detections that have
        a confidence lower than this value.
    nms_max_overlap: float
        Maximum detection overlap (non-maxima suppression threshold).
    min_detection_height : int
        Detection height threshold. Disregard all detections that have
        a height lower than this value.
    max_cosine_distance : float
        Gating threshold for cosine distance metric (object appearance).
    nn_budget : Optional[int]
        Maximum size of the appearance descriptor gallery. If None, no budget
        is enforced.
    display : bool
        If True, show visualization of intermediate tracking results.

    """
    logging.debug(f"min_confidence = {min_confidence}")

    seq_info = gather_sequence_info(sequence_dir, detection_file)
    metric = nn_matching.NearestNeighborDistanceMetric(
        'cosine',
        max_cosine_distance,
        nn_budget
    )
    tracker = Tracker(metric)
    results = []
    model = YOLO("yolov8m.pt")

    if opt.iou_only or opt.LiteSORT or opt.precomputed_features:
        reid_model = None
    else:
        reid_model = load_reid_model() if opt.BoT else load_deep_sort_model()
    # reid_model = load_deep_sort_model()

    tick = time.time()

    # inner function
    def frame_callback(vis, frame_idx):
        # print("Processing frame %05d" % frame_idx)

        # Load image and generate detections.

        if opt.precomputed_features:
            detections = create_detections_original(
                seq_info["detections"], frame_idx, min_detection_height)
        else:
            detections = create_detections(
                sequence_dir, frame_idx, model, min_detection_height, reid_model)

        detections = [d for d in detections if d.confidence >= min_confidence]

        # Run non-maxima suppression.
        boxes = np.array([d.tlwh for d in detections])
        scores = np.array([d.confidence for d in detections])
        indices = preprocessing.non_max_suppression(
            boxes, nms_max_overlap, scores)
        detections = [detections[i] for i in indices]

        # Update tracker.
        if opt.ECC:
            tracker.camera_update(sequence_dir.split('/')[-1], frame_idx)

        tracker.predict()
        tracker.update(detections)

        # Update visualization.
        if display:
            image = cv2.imread(
                seq_info["image_filenames"][frame_idx], cv2.IMREAD_COLOR)
            vis.set_image(image.copy())
            vis.draw_detections(detections)
            vis.draw_trackers(tracker.tracks)
            vis.put_metadata()
            vis.save_visualization()

        # Store results.
        for track in tracker.tracks:
            if not track.is_confirmed() or track.time_since_update > 1:
                continue
            bbox = track.to_tlwh()
            results.append([
                frame_idx, track.track_id, bbox[0], bbox[1], bbox[2], bbox[3]])

    # Run tracker.
    if display:

        visualizer = visualization.Visualization(
            seq_info, update_ms=5, dir_save=opt.dir_save)
    else:
        visualizer = visualization.NoVisualization(seq_info)
    visualizer.run(frame_callback)

    if opt.dataset in ['MOT17', 'MOT20']:
        # Store results.
        f = open(output_file, 'w')
        for row in results:
            print('%d,%d,%.2f,%.2f,%.2f,%.2f,1,-1,-1,-1' % (
                row[0], row[1], row[2], row[3], row[4], row[5]), file=f)
    elif opt.dataset == 'KITTI':
        with open(output_file, 'w') as f:
            for row in results:
                # Set default values for fields that might not be available in your tracker
                object_type = "Pedestrian"  # or your default
                truncated = -1  # default, as this info might not be available
                occluded = -1  # default, as this info might not be available
                alpha = -10  # default, as this info might not be available
                # default, as this info might not be available
                dimensions = (-1, -1, -1)
                # default, as this info might not be available
                location = (-1000, -1000, -1000)
                rotation_y = -10  # default, as this info might not be available
                score = row[5]  # if you have confidence score

                # Write formatted data with maximum 2 decimal places for floating-point values
                f.write(f"{row[0]} {row[1]} {object_type} {truncated} {occluded} {alpha:.2f} "
                        f"{row[2]:.2f} {row[3]:.2f} {(row[2]+row[4]):.2f} {(row[3]+row[5]):.2f} "
                        f"{' '.join(map(lambda l: f'{l:.2f}', location))} "
                        f"{' '.join(map(lambda d: f'{d:.2f}', dimensions))} \n"
                        )

    tock = time.time()
    time_spent_for_the_sequence = tock - tick
    time_info_s = f'time: {time_spent_for_the_sequence:.0f}s'

    num_frames = (seq_info["max_frame_idx"] - seq_info["min_frame_idx"])
    avg_time_per_frame = (time_spent_for_the_sequence) / num_frames

    print(
        f'{time_info_s} | Avg FPS: {1/avg_time_per_frame:.1f}')


def bool_string(input_string):
    if input_string not in {"True", "False"}:
        raise ValueError("Please Enter a valid Ture/False choice")
    else:
        return (input_string == "True")


def parse_args():
    """ Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="Deep SORT")
    parser.add_argument(
        "--sequence_dir", help="Path to MOTChallenge sequence directory",
        default='datasets/MOT17', required=True)
    parser.add_argument(
        "--detection_file", help="Path to custom detections.", default=None,
        required=True)
    parser.add_argument(
        "--output_file", help="Path to the tracking output file. This file will"
        " contain the tracking results on completion.",
        default="/tmp/hypotheses.txt")
    parser.add_argument(
        "--min_confidence", help="Detection confidence threshold. Disregard "
        "all detections that have a confidence lower than this value.",
        default=0.8, type=float)
    parser.add_argument(
        "--min_detection_height", help="Threshold on the detection bounding "
        "box height. Detections with height smaller than this value are "
        "disregarded", default=0, type=int)
    parser.add_argument(
        "--nms_max_overlap",  help="Non-maxima suppression threshold: Maximum "
        "detection overlap.", default=1.0, type=float)
    parser.add_argument(
        "--max_cosine_distance", help="Gating threshold for cosine distance "
        "metric (object appearance).", type=float, default=0.2)
    parser.add_argument(
        "--nn_budget", help="Maximum size of the appearance descriptors "
        "gallery. If None, no budget is enforced.", type=int, default=None)
    parser.add_argument(
        "--display", help="Show intermediate tracking results",
        default=True, type=bool_string)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(
        args.sequence_dir, args.detection_file, args.output_file,
        args.min_confidence, args.nms_max_overlap, args.min_detection_height,
        args.max_cosine_distance, args.nn_budget, args.display)
