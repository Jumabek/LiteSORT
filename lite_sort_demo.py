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
    nms_max_overlap = 1.0
    metric = nn_matching.NearestNeighborDistanceMetric(
        'cosine',
        0.3,
        100
    )

    tracker = Tracker(metric)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Process each frame
        yolo_results = model.predict(
            frame, classes=[0], verbose=False, imgsz=1280, yolosort=True, conf=.25)

        boxes = yolo_results[0].boxes.data.cpu().numpy()
        for box in boxes:
            xmin, ymin, xmax, ymax, conf, _ = box
            xmin, ymin, xmax, ymax = int(xmin), int(ymin), int(xmax), int(ymax)
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (255, 0, 0), 2)

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
        # Draw the bounding boxes for tracker
        for track in tracker.tracks:
            if not track.is_confirmed() or track.time_since_update > 1:
                continue

            bbox = track.to_tlwh()
            x, y, w, h = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, str(track.track_id), (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                        0.75, (0, 255, 0), 2)

        # Display the frame
        cv2.imshow('Frame', frame)

        # Press Q on keyboard to exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def main():

    process_video(
        'VIRAT_S_010204_07_000942_000989.mp4')


if __name__ == "__main__":
    main()
