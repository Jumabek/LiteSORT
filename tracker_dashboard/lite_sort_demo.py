import cv2
import sys
import argparse
from ultralytics import YOLO
from deep_sort.detection import Detection
from application_util import preprocessing
from deep_sort.tracker import Tracker
from deep_sort import nn_matching

import numpy as np


def process_video(video_path):

    # Open the video file or camera
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    model = YOLO("yolov8m.pt")
    print(model.info(verbose=True))

    nms_max_overlap = 1.0
    metric = nn_matching.NearestNeighborDistanceMetric(
        'cosine',
        0.3,
        100
    )

    tracker = Tracker(metric)

    frame_number = 0  # Initialize frame number

    # Get video frame width and height
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Get total number of frames in the video ADDED
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Create VideoWriter object ADDED
    out = cv2.VideoWriter('output_video.avi', cv2.VideoWriter_fourcc(*'XVID'), 30, (frame_width, frame_height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_number += 1  # Increment frame number

        # Printing number of frames ADDED
        print(f"Processing frame {frame_number}/{total_frames} ({frame_number/total_frames:.2%})")


        # Process each frame
        yolo_results = model.predict(
            frame, classes=[0], verbose=False, imgsz=1280, appearance_feature_layer='layer0', conf=.25)

        boxes = yolo_results[0].boxes.data.cpu().numpy()
        for box in boxes:
            xmin, ymin, xmax, ymax, conf, _ = box
            xmin, ymin, xmax, ymax = int(xmin), int(ymin), int(xmax), int(ymax)
            cv2.rectangle(frame, (xmin, ymin),
                          (xmax, ymax), (255, 0, 0), 2)

        appearance_features = yolo_results[0].appearance_features.cpu().numpy()
        detections = []
        for box, feature in zip(boxes, appearance_features):
            xmin, ymin, xmax, ymax, conf, _ = box
            x_tl = xmin
            y_tl = ymin
            width = xmax - xmin
            height = ymax - ymin
            bbox = (x_tl, y_tl, width, height)
            detection = Detection(bbox, conf, feature)

            detections.append(detection)

        # Run non-maxima suppression.
        boxes = np.array([d.tlwh for d in detections])
        scores = np.array([d.confidence for d in detections])
        indices = preprocessing.non_max_suppression(
            boxes, nms_max_overlap, scores)
        detections = [detections[i] for i in indices]

        tracker.predict()
        tracker.update(detections)

        # Draw the bounding boxes for tracker
        for track in tracker.tracks:
            if not track.is_confirmed() or track.time_since_update > 1:
                continue

            bbox = track.to_tlwh()
            x, y, w, h = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])

            cv2.rectangle(frame, (x, y),
                          (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, str(track.track_id), (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                        0.75, (0, 255, 0), 2)

        # Write the frame to the output video ADDED
        out.write(frame)

    # Release resources
    cap.release()
    out.release() # ADDED
    cv2.destroyAllWindows()


def main():
    process_video(
        'VIRAT_S_010204_07_000942_000989.mp4') # path is set


if __name__ == "__main__":
    main()
