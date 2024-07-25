#!/bin/bash

# List of resolutions and confidence thresholds
RESOLUTIONS=(1280)
CONFIDENCES=(.25)
BENCHMARK="DanceTrack" 

# Base Commandx 
BASE_CMD="python3 TrackEval/scripts/run_mot_challenge.py"

# Parent directory where all trackers' results are stored
PARENT_TRACKERS_FOLDER="results/off-the-shelf/DanceTrack-train"

# SORT__input_1280__conf_.25 LiteSORT__input_1280__conf_.25 DeepSORT__input_1280__conf_.25 StrongSORT__input_1280__conf_.25

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
                    --SPLIT_TO_EVAL train \
                    --TRACKERS_TO_EVAL LITE_BOTSORT__input_1280__conf_.25 LITE_DEEPOCSORT__input_1280__conf_.25 \
                    --TRACKER_SUB_FOLDER data \
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

        # Run the evaluation for the current combination of resolution and confidence
        eval $EVAL_CMD > "${PARENT_TRACKERS_FOLDER}/${BENCHMARK}_LITE_evaluation_${res}_conf_${conf}.txt"
    done
done

echo "Evaluation script completed."
