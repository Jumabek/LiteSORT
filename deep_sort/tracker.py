# vim: expandtab:ts=4:sw=4
from __future__ import absolute_import
import numpy as np
from . import kalman_filter
from . import linear_assignment
from . import iou_matching
from .track import Track
from opts import opt


class Tracker:
    """
    This is the multi-target tracker.

    Parameters
    ----------
    metric : nn_matching.NearestNeighborDistanceMetric
        A distance metric for measurement-to-track association.
    max_age : int
        Maximum number of missed misses before a track is deleted.
    n_init : int
        Number of consecutive detections before the track is confirmed. The
        track state is set to `Deleted` if a miss occurs within the first
        `n_init` frames.

    Attributes
    ----------
    metric : nn_matching.NearestNeighborDistanceMetric
        The distance metric used for measurement to track association.
    max_age : int
        Maximum number of missed misses before a track is deleted.
    n_init : int
        Number of frames that a track remains in initialization phase.
    tracks : List[Track]
        The list of active tracks at the current time step.

    """

    def __init__(self, metric, max_iou_distance=.7, max_age=30, n_init=3):

        self.metric = metric
        self.max_iou_distance = max_iou_distance
        self.max_age = max_age
        self.n_init = n_init

        self.tracks = []
        self._next_id = 1

    def predict(self):
        """Propagate track state distributions one time step forward.

        This function should be called once every time step, before `update`.
        """
        for track in self.tracks:
            track.predict()

    def camera_update(self, video, frame):
        for track in self.tracks:
            track.camera_update(video, frame)

    def update(self, detections):
        """Perform measurement update and track management.

        Parameters
        ----------
        detections : List[deep_sort.detection.Detection]
            A list of detections at the current time step.

        """
        # Run matching cascade.
        matches, unmatched_tracks, unmatched_detections = self._match(
            detections)

        # Update track set.
        for track_idx, detection_idx in matches:
            self.tracks[track_idx].update(detections[detection_idx])
        for track_idx in unmatched_tracks:
            self.tracks[track_idx].mark_missed()
        for detection_idx in unmatched_detections:
            self._initiate_track(detections[detection_idx])
        self.tracks = [t for t in self.tracks if not t.is_deleted()]

        # Update distance metric.
        active_targets = [t.track_id for t in self.tracks]
        features, targets = [], []
        for track in self.tracks:

            features += track.features
            targets += [track.track_id for _ in track.features]
            if not opt.EMA:
                track.features = []
        # updates apperance (ReID) feature bank
        self.metric.partial_fit(
            np.asarray(features), np.asarray(targets), active_targets)

    def _match(self, detections):
        # iou only matching
        if opt.tracker_name == "SORT":
            # If IOU_ONLY flag is set, skip the appearance feature matching and perform only IOU matching.
            matches, unmatched_tracks, unmatched_detections = \
                linear_assignment.min_cost_matching(
                    iou_matching.iou_cost, self.max_iou_distance, self.tracks,
                    detections)
            return matches, unmatched_tracks, unmatched_detections

        def gated_metric(tracks, dets, track_indices, detection_indices):
            features = np.array(
                [dets[i].feature for i in detection_indices])  # (18,emd_dim)
            targets = np.array(
                [tracks[i].track_id for i in track_indices])  # (10,)
            cost_matrix = self.metric.distance(features, targets)
            # if not opt.appearance_only_matching:
            cost_matrix = linear_assignment.gate_cost_matrix(
                cost_matrix, tracks, dets, track_indices,
                detection_indices)
            return cost_matrix

        if opt.appearance_only_matching:
            # Only use appearance features for matching
            track_indices = np.arange(len(self.tracks))
            detection_indices = np.arange(len(detections))
            matches, unmatched_tracks, unmatched_detections = \
                linear_assignment.min_cost_matching(
                    gated_metric, self.max_iou_distance, self.tracks,
                    detections, track_indices, detection_indices)
            return matches, unmatched_tracks, unmatched_detections

        # below code first matches using apperance features, then it matches using iou cost for deepsort
        # Split track set into confirmed (will be used for appearance-based matching) and unconfirmed tracks.
        confirmed_tracks = [
            i for i, t in enumerate(self.tracks) if t.is_confirmed()]
        unconfirmed_tracks = [
            i for i, t in enumerate(self.tracks) if not t.is_confirmed()]

        # Associate confirmed tracks using appearance features.
        matches_a, unmatched_tracks_a, unmatched_detections = \
            linear_assignment.matching_cascade(
                gated_metric, self.metric.matching_threshold, self.max_age,
                self.tracks, detections, confirmed_tracks)

        # Associate remaining tracks together with unconfirmed tracks using IOU.
        iou_track_candidates = unconfirmed_tracks + [
            k for k in unmatched_tracks_a if
            self.tracks[k].time_since_update == 1]
        unmatched_tracks_a = [
            k for k in unmatched_tracks_a if
            self.tracks[k].time_since_update != 1]
        matches_b, unmatched_tracks_b, unmatched_detections = \
            linear_assignment.min_cost_matching(
                iou_matching.iou_cost, self.max_iou_distance, self.tracks,
                detections, iou_track_candidates, unmatched_detections)

        matches = matches_a + matches_b
        unmatched_tracks = list(
            set(unmatched_tracks_a + unmatched_tracks_b))

        return matches, unmatched_tracks, unmatched_detections

    def _initiate_track(self, detection):
        self.tracks.append(Track(
            detection.to_xyah(), self._next_id, self.n_init, self.max_age,
            detection.feature, detection.confidence))
        self._next_id += 1
