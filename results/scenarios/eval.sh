#!/bin/bash

# List of resolutions, confidence thresholds, and trackers
RESOLUTIONS=(1280)
CONFIDENCES=(.25)
TRACKERS=("DeepSORT" "StrongSORT" "LiteSORT")
BENCHMARK="MOT20" 
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
            TRACKER_PATH="/root/LiteSORT/results/scenarios/MOT20/${tracker}__input_${res}__conf_${conf}"

            # Check if the tracker folder exists
            if [ -d "${TRACKER_PATH}" ]; then
                echo "Running evaluation for the specified tracker folder: ${TRACKER_PATH}"

                # Construct the command
                EVAL_CMD="${BASE_CMD} \
                    --BENCHMARK ${BENCHMARK} \
                    --SPLIT_TO_EVAL train \
                    --TRACKERS_TO_EVAL "/root/LiteSORT/results" \
                    --TRACKER_SUB_FOLDER  "scenarios/MOT20/${tracker}__input_${res}__conf_${conf}" \
                    --METRICS HOTA CLEAR Identity VACE \
                    --USE_PARALLEL False \
                    --NUM_PARALLEL_CORES 32 \
                    --GT_LOC_FORMAT '{gt_folder}/{seq}/gt/gt.txt' \
                    --OUTPUT_SUMMARY True \
                    --OUTPUT_EMPTY_CLASSES False \
                    --OUTPUT_DETAILED False \
                    --PLOT_CURVES False"

                # Print the evaluation command
                #echo "Evaluation command: ${EVAL_CMD}"

                # Run the evaluation and store the output in a file inside the tracker folder
                eval $EVAL_CMD > "${TRACKER_PATH}/evaluation_output.txt"
            else
                echo "WARNING: Tracker folder ${TRACKER_PATH} does not exist. Skipping evaluation."
            fi
        done
    done
done

echo "Evaluation script completed."