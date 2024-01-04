#!/bin/bash

# List of resolutions, confidence thresholds, and trackers
RESOLUTIONS=(1280)
CONFIDENCES=(.25)
TRACKERS=("DeepSORT" "StrongSORT" "LiteSORT" "StrongSORT")
BENCHMARK="KITTI" 
# Base Command
BASE_CMD="python TrackEval/scripts/run_kitti.py"

echo "Starting the evaluation script..."

# For every combination of resolution, confidence, and tracker, run the evaluation
for tracker in "${TRACKERS[@]}"; do
    for res in "${RESOLUTIONS[@]}"; do
        for conf in "${CONFIDENCES[@]}"; do
            # Debug messages
            echo "-------------------------------------------"
            echo "Processing tracker: ${tracker}, resolution: ${res}, and confidence: ${conf}"

            # Tracker folder for the current combination of tracker, resolution, and confidence
            TRACKER_PATH="/home/juma/code/StrongSORT/results/scenarios/${BENCHMARK}/${tracker}__input_${res}__conf_${conf}"

            # Check if the tracker folder exists
            if [ -d "${TRACKER_PATH}" ]; then
                echo "Running evaluation for the specified tracker folder: ${TRACKER_PATH}"

                # Construct the command
                EVAL_CMD="${BASE_CMD}" 

                # Print the evaluation command
                echo "Evaluation command: ${EVAL_CMD}"

                # Run the evaluation and store the output in a file inside the tracker folder
                eval $EVAL_CMD > "${TRACKER_PATH}/evaluation_output.txt"
            else
                echo "WARNING: Tracker folder ${TRACKER_PATH} does not exist. Skipping evaluation."
            fi
        done
    done
done

echo "Evaluation script completed."
