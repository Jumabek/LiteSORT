#!/bin/bash

# List of resolutions and confidence thresholds
RESOLUTIONS=(1280)
CONFIDENCES=(.25)
BENCHMARK="person_path_22" 

# Base Commandx 
BASE_CMD="python TrackEval/scripts/run_person_path_22.py"

# Parent directory where all trackers' results are stored
PARENT_TRACKERS_FOLDER="results/off-the-shelf"

echo "Starting the evaluation script..."

# For every combination of resolution and confidence, run the evaluation
for res in "${RESOLUTIONS[@]}"; do
    for conf in "${CONFIDENCES[@]}"; do
        # Debug messages
        echo "-------------------------------------------"
        echo "Processing resolution: ${res}, and confidence: ${conf}"

        # Construct the command
        EVAL_CMD="${BASE_CMD} \
                    --BENCHMARK ${BENCHMARK} \
                    --TRACKERS_FOLDER ${PARENT_TRACKERS_FOLDER} \
                    --SPLIT_TO_EVAL test \
                    --TRACKERS_TO_EVAL BoTSORT__input_1280__conf_.25 ByteTRACK__input_1280__conf_.25 DeepOC-SORT__input_1280__conf_.25 OCSORT__input_1280__conf_.25 \
                    --TRACKER_SUB_FOLDER data \
                    --METRICS HOTA CLEAR Identity VACE \
                    --USE_PARALLEL True \
                    --NUM_PARALLEL_CORES 95 \
                    --GT_LOC_FORMAT '{gt_folder}/{seq}/gt/gt.txt' \
                    --OUTPUT_SUMMARY True \
                    --OUTPUT_EMPTY_CLASSES False \
                    --OUTPUT_DETAILED True \
                    --PLOT_CURVES True"

        # Print the evaluation command
        echo "Evaluation command: ${EVAL_CMD}"

        # Run the evaluation for the current combination of resolution and confidence
        eval $EVAL_CMD #> "${PARENT_TRACKERS_FOLDER}/evaluation_output_res_${res}_conf_${conf}.txt"
    done
done

echo "Evaluation script completed."
