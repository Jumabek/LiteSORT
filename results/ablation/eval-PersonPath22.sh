#!/bin/bash

# List of resolutions and confidence thresholds
RESOLUTIONS=(1280)
CONFIDENCES=(.25)
BENCHMARK="PersonPath22"
SPLIT="test" 

# Base Command
BASE_CMD="python TrackEval/scripts/run_person_path_22.py --NUM_PARALLEL_CORES 50 --TRACKERS_FOLDER "

# Parent directory where all trackers' results are stored
PARENT_TRACKERS_FOLDER="/workspace/LiteSORT/results/scenarios/${BENCHMARK}"

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
        eval $EVAL_CMD > "/workspace/LiteSORT/results/scenarios/${BENCHMARK}-${SPLIT}.txt"
    done
done

echo "Evaluation script completed."
