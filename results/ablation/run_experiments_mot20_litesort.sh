#!/bin/bash

# Hardcoded Variables
EXPERIMENT_NAME="scenarios"
DATASET="MOT20"

# Base Command
BASE_CMD="python strong_sort.py ${DATASET} train "

# Function to run LiteSORT tracker with layer specification
run_tracker() {
    TRACKER_NAME="LiteSORT"  # Tracker name is fixed to LiteSORT
    INPUT_RESOLUTION=$1
    MIN_CONFIDENCE=$2
    APPEARANCE_LAYER=$3  # New argument for the appearance feature layer

    echo "-----------------------------------"
    echo "Running tracker: ${TRACKER_NAME} with Input Resolution: ${INPUT_RESOLUTION}, Confidence Threshold: ${MIN_CONFIDENCE}, and Appearance Feature Layer: ${APPEARANCE_LAYER}"  # Debug message

    DIR_SAVE="results/${EXPERIMENT_NAME}/${DATASET}-train/woGating_${APPEARANCE_LAYER}_${TRACKER_NAME}__input_${INPUT_RESOLUTION}__conf_${MIN_CONFIDENCE}/data/"
    if [ ! -d "${DIR_SAVE}" ]; then
        mkdir -p ${DIR_SAVE}
    fi

    CMD="${BASE_CMD} LiteSORT --dir_save ${DIR_SAVE} --input_resolution ${INPUT_RESOLUTION} --min_confidence ${MIN_CONFIDENCE} --appearance_feature_layer ${APPEARANCE_LAYER} "
    echo "Executing command: ${CMD}"
    eval ${CMD}

    echo "Experiment completed for ${TRACKER_NAME} with ${APPEARANCE_LAYER}!"
}

# Iterate over specific resolutions, confidence thresholds, and appearance layers
for INPUT_RESOLUTION in 1280; do
    for MIN_CONFIDENCE in .25; do
        for LAYER in 0 1 3 5 7; do
            APPEARANCE_LAYER="layer${LAYER}"
            run_tracker ${INPUT_RESOLUTION} ${MIN_CONFIDENCE} ${APPEARANCE_LAYER}
        done
    done
done
