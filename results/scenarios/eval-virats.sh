#!/bin/bash

# List of resolutions and confidence thresholds
RESOLUTIONS=(1280)
CONFIDENCES=(.25)
BENCHMARK="VIRAT-S" 

# Base Command
BASE_CMD="python TrackEval/scripts/run_mot_challenge.py"

# Parent directory where all trackers' results are stored
PARENT_TRACKERS_FOLDER="/home/juma/code/StrongSORT/results/scenarios"

echo "Starting the evaluation script..."

# Construct the command
EVAL_CMD="${BASE_CMD} \
            --BENCHMARK ${BENCHMARK} \
            --TRACKERS_FOLDER ${PARENT_TRACKERS_FOLDER} \
            --SPLIT_TO_EVAL train \
            --METRICS HOTA CLEAR Identity VACE \
            --USE_PARALLEL True \
            --NUM_PARALLEL_CORES 16 \
            --GT_LOC_FORMAT '{gt_folder}/{seq}/gt/gt.txt' \
            --OUTPUT_SUMMARY True \
            --OUTPUT_EMPTY_CLASSES False \
            --OUTPUT_DETAILED True \
            --PLOT_CURVES True \
            --GT_FOLDER datasets/VIRAT-S"

# Print the evaluation command
echo "Evaluation command: ${EVAL_CMD}"

# Run the evaluation for the current combination of resolution and confidence
eval $EVAL_CMD #> "${PARENT_TRACKERS_FOLDER}/evaluation_output_res_${res}_conf_${conf}.txt"

echo "Evaluation script completed."
