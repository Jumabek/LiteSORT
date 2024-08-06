#!/bin/bash

# List of resolutions and confidence thresholds
RESOLUTIONS=(1280)
CONFIDENCES=(.25)
BENCHMARK="DanceTrack"

# Base Command
BASE_CMD="python3 TrackEval/scripts/run_mot_challenge.py"

# Parent directory where all trackers' results are stored
PARENT_TRACKERS_FOLDER="yolo_tracking/hbai_scripts/DanceTrack-train_fixed_format"

echo "Starting the evaluation script..."

# IOU values
IOU_VALUES=(0.2 0.25 0.3 0.35 0.4 0.45 0.5 0.55 0.6 0.65 0.7 0.75 0.8)

# For every combination of resolution, confidence, and iou, run the evaluation
for res in "${RESOLUTIONS[@]}"; do
    for conf in "${CONFIDENCES[@]}"; do
        for iou in "${IOU_VALUES[@]}"; do
            # Debug messages
            echo "-------------------------------------------"
            echo "Processing resolution: ${res}, confidence: ${conf}, and iou: ${iou}"

            # Construct the command
            EVAL_CMD="${BASE_CMD} \
                        --BENCHMARK ${BENCHMARK} \
                        --TRACKERS_FOLDER ${PARENT_TRACKERS_FOLDER} \
                        --SPLIT_TO_EVAL train \
                        --TRACKER_SUB_FOLDER data \
                        --TRACKERS_TO_EVAL deepocsort__input_${res}__conf_${conf}__IoU_${iou} ocsort__input_${res}__conf_${conf}__IoU_${iou} \
                        --METRICS HOTA CLEAR Identity VACE \
                        --USE_PARALLEL True \
                        --NUM_PARALLEL_CORES 16 \
                        --GT_LOC_FORMAT '{gt_folder}/{seq}/gt/gt.txt' \
                        --OUTPUT_SUMMARY True \
                        --OUTPUT_EMPTY_CLASSES False \
                        --OUTPUT_DETAILED True \
                        --PLOT_CURVES True \
                        --GT_FOLDER '/media/hbai/data/code/LiteSORT/datasets/DanceTrack/train' \
                        --SKIP_SPLIT_FOL True \
                        --SEQMAP_FILE '/media/hbai/data/code/LiteSORT/datasets/DanceTrack/train_seqmap.txt' \
                        "

            # Print the evaluation command
            echo "Evaluation command: ${EVAL_CMD}"

            # Run the evaluation for the current combination of resolution, confidence, and iou
            eval $EVAL_CMD > "${PARENT_TRACKERS_FOLDER}/${BENCHMARK}_evaluation_${res}_conf_${conf}_${iou}.txt"
        done
    done
done

echo "Evaluation script completed."
