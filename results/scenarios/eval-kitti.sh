#!/bin/bash

# List of resolutions and confidence thresholds
RESOLUTIONS=(1280)
CONFIDENCES=(.25)
BENCHMARK="KITTI" 

# Base Command
BASE_CMD="python TrackEval/scripts/run_kitti.py --TRACKERS_FOLDER"

# Parent directory where all trackers' results are stored
PARENT_TRACKERS_FOLDER="/home/juma/code/StrongSORT/results/scenarios/${BENCHMARK}"

echo "Starting the evaluation script..."

# For every combination of resolution and confidence, run the evaluation
for res in "${RESOLUTIONS[@]}"; do
    for conf in "${CONFIDENCES[@]}"; do
        # Debug messages
        echo "-------------------------------------------"
        echo "Processing resolution: ${res}, and confidence: ${conf}"

        # Construct the command
        EVAL_CMD="${BASE_CMD} ${PARENT_TRACKERS_FOLDER}"

        # Print the evaluation command
        echo "Evaluation command: ${EVAL_CMD}"

        # Run the evaluation for the current combination of resolution and confidence
        eval $EVAL_CMD > "${PARENT_TRACKERS_FOLDER}/evaluation_output_res_${res}_conf_${conf}.txt"
    done
done

echo "Evaluation script completed."
