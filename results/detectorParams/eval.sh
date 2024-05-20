#!/bin/bash

#
# List of resolutions, confidence thresholds, and trackers
RESOLUTIONS=(320 640 960 1280 1600 1920 2240 2560)
#CONFIDENCES=(.25 .3 .35 .4 .45 .5 .55 .6 .65 .7)
CONFIDENCES=(.05 .1 .15 .2)
#CONFIDENCES=(.3)

TRACKERS=("SORT" "LiteSORT" "DeepSORT" "StrongSORT")

# Base Command
BASE_CMD="python TrackEval/scripts/run_mot_challenge.py"

echo "Starting the evaluation script..."

# For every combination of resolution, confidence, and tracker, run the evaluation
for tracker in "${TRACKERS[@]}"; do
    for res in "${RESOLUTIONS[@]}"; do
        for conf in "${CONFIDENCES[@]}"; do
            # Debug messages
            echo "-------------------------------------------"
            echo "Processing tracker: ${tracker}, resolution: ${res}, and confidence: ${conf}"

            # Tracker folder for the current combination of tracker, resolution, and confidence
            TRACKER_PATH="/home/juma/code/StrongSORT/results/detectorParams/runs/${tracker}__input_${res}__conf_${conf}"

            # Check if the tracker folder exists
            if [ -d "${TRACKER_PATH}" ]; then
                echo "Running evaluation for the specified tracker folder: ${TRACKER_PATH}"

                # Run the evaluation and store the output in a file inside the tracker folder
                ${BASE_CMD} \
                    --BENCHMARK MOT17 \
                    --SPLIT_TO_EVAL train \
                    --TRACKERS_TO_EVAL ${TRACKER_PATH} \
                    --TRACKER_SUB_FOLDER '' \
                    --METRICS HOTA CLEAR Identity VACE \
                    --USE_PARALLEL False \
                    --NUM_PARALLEL_CORES 16 \
                    --GT_LOC_FORMAT '{gt_folder}/{seq}/gt/gt.txt' \
                    --OUTPUT_SUMMARY True \
                    --OUTPUT_EMPTY_CLASSES False \
                    --OUTPUT_DETAILED False \
                    --PLOT_CURVES False \
                    > "${TRACKER_PATH}/evaluation_output.txt"
            else
                echo "WARNING: Tracker folder ${TRACKER_PATH} does not exist. Skipping evaluation."
            fi
        done
    done
done

echo "Evaluation script completed."
