# vim: expandtab:ts=4:sw=4
import cv2
import numpy as np
import colorsys
from .image_viewer import ImageViewer
import ntpath
from opts import opt
import time


def create_unique_color_float(tag, hue_step=0.41):
    """Create a unique RGB color code for a given track id (tag).

    The color code is generated in HSV color space by moving along the
    hue angle and gradually changing the saturation.

    Parameters
    ----------
    tag : int
        The unique target identifying tag.
    hue_step : float
        Difference between two neighboring color codes in HSV space (more
        specifically, the distance in hue channel).

    Returns
    -------
    (float, float, float)
        RGB color code in range [0, 1]

    """
    h, v = (tag * hue_step) % 1, 1. - (int(tag * hue_step) % 4) / 5.
    r, g, b = colorsys.hsv_to_rgb(h, 1., v)
    return r, g, b


def create_unique_color_uchar(tag, hue_step=0.41):
    """Create a unique RGB color code for a given track id (tag).

    The color code is generated in HSV color space by moving along the
    hue angle and gradually changing the saturation.

    Parameters
    ----------
    tag : int
        The unique target identifying tag.
    hue_step : float
        Difference between two neighboring color codes in HSV space (more
        specifically, the distance in hue channel).

    Returns
    -------
    (int, int, int)
        RGB color code in range [0, 255]

    """
    r, g, b = create_unique_color_float(tag, hue_step)
    return int(255*r), int(255*g), int(255*b)


class NoVisualization(object):
    """
    A dummy visualization object that loops through all frames in a given
    sequence to update the tracker without performing any visualization.
    """

    def __init__(self, seq_info):
        self.frame_idx = seq_info["min_frame_idx"]
        self.last_idx = seq_info["max_frame_idx"]

    def set_image(self, image):
        pass

    def draw_groundtruth(self, track_ids, boxes):
        pass

    def draw_detections(self, detections):
        pass

    def draw_trackers(self, trackers):
        pass

    def run(self, frame_callback):
        while self.frame_idx <= self.last_idx:
            frame_callback(self, self.frame_idx)
            self.frame_idx += 1


class Visualization(object):
    """
    This class shows tracking output in an OpenCV image viewer.
    """

    def __init__(self, seq_info, update_ms, dir_save, display=False):
        image_shape = seq_info["image_size"][::-1]
        aspect_ratio = float(image_shape[1]) / image_shape[0]
        image_shape = 1024, int(aspect_ratio * 1024)
        self.viewer = ImageViewer(
            update_ms, image_shape, "Figure %s" % seq_info["sequence_name"], display=display)
        self.viewer.thickness = 2
        self.frame_idx = seq_info["min_frame_idx"]
        self.last_idx = seq_info["max_frame_idx"]
        self.last_frame_update_time = time.time()
        # Initialize the video writer
        import os

        self.tracker_name = opt.tracker_name
        self.display = display

        # Check if folder exists, if not create one
        if not os.path.exists(dir_save):
            os.makedirs(dir_save)
        self.img_size_for_video_writer = image_shape  # (2*640, 2*480)
        # self.video_writer = cv2.VideoWriter(
        #     f'{dir_save}/{seq_info["sequence_name"]}.avi',
        #     cv2.VideoWriter_fourcc(*'DIVX'),
        #     20.0,
        #     self.img_size_for_video_writer
        # )
        self.video_writer = cv2.VideoWriter(
            f'{dir_save}/{seq_info["sequence_name"]}.mp4',  # Change the file extension to .mp4
            cv2.VideoWriter_fourcc(*'mp4v'),  # Change the codec to 'XVID' or another MP4 compatible codec
            30.0,
            self.img_size_for_video_writer
        )



        if not self.video_writer.isOpened():
            print("Error: Video writer not initialized!")

    def run(self, frame_callback):
    
        self.viewer.run(lambda: self._update_fun(frame_callback))
        
    def _update_fun(self, frame_callback):
        if self.frame_idx > self.last_idx:
            self.video_writer.release()
            return False  # Terminate
        tick = time.time()
        frame_callback(self, self.frame_idx)
        tock = time.time()
        elapsed_time = tock - tick
        if elapsed_time > 0:
            self.viewer.fps = round(1 / elapsed_time, 1)

        self.frame_idx += 1
        return True

  

    def set_image(self, image):
        self.viewer.image = image

    def draw_groundtruth(self, track_ids, boxes):
        self.viewer.thickness = 2
        for track_id, box in zip(track_ids, boxes):
            self.viewer.color = create_unique_color_uchar(track_id)
            self.viewer.rectangle(*box.astype(int), label=str(track_id))

    def draw_detections(self, detections):
        self.viewer.thickness = 2
        self.viewer.color = 0, 0, 255
        for i, detection in enumerate(detections):
            self.viewer.rectangle(*detection.tlwh)

    def draw_trackers(self, tracks):
        self.viewer.thickness = 2
        for track in tracks:
            if not track.is_confirmed() or track.time_since_update > 0:
                continue
            self.viewer.color = create_unique_color_uchar(track.track_id)
            self.viewer.rectangle(
                *track.to_tlwh().astype(int), label=str(track.track_id))
            # self.viewer.gaussian(track.mean[:2], track.covariance[:2, :2],
            #                      label="%d" % track.track_id)

    def put_metadata(self):
        # Obtain the image from viewer
        image = self.viewer.image
        font_scale = 2.5
        thickness = 5
        # Add tracker name to the visualization
        cv2.putText(image, "Tracker: " + self.tracker_name, (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 0, 0), thickness)

        # Add frame id to the visualization
        cv2.putText(image, "Frame ID: " + str(self.frame_idx),
                    (10, 160), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), thickness)
        cv2.putText(image, "FPS: " + str(self.viewer.fps),
                    (10, 260), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)

    def save_visualization(self):
        # Resize and write the image to the video writer
        image = self.viewer.image.copy()
        resized_image = cv2.resize(image, self.img_size_for_video_writer)
        self.video_writer.write(resized_image)
