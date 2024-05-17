#!/bin/bash

# Hardcoded Variables
EXPERIMENT_NAME="scenarios"
DATASET="MOT17"

# Base Command
BASE_CMD="python strong_sort.py ${DATASET} train "

# Function to run LiteSORT tracker with layer specification
run_tracker() {
    TRACKER_NAME="LiteSORT"  # Tracker name is fixed to LiteSORT
    INPUT_RESOLUTION=$1
    MIN_CONFIDENCE=$2
    APPEARANCE_LAYER=$3
    MAX_COSINE_DISTANCE=$4  # New argument for the max cosine distance

    echo "-----------------------------------"
    echo "Running tracker: ${TRACKER_NAME} with Input Resolution: ${INPUT_RESOLUTION}, Confidence Threshold: ${MIN_CONFIDENCE}, Appearance Feature Layer: ${APPEARANCE_LAYER}, Max Cosine Distance: ${MAX_COSINE_DISTANCE}"  # Updated debug message

    DIR_SAVE="results/${EXPERIMENT_NAME}/${DATASET}-train/reidOnly_${APPEARANCE_LAYER}_${TRACKER_NAME}__input_${INPUT_RESOLUTION}__conf_${MIN_CONFIDENCE}__cosdist_${MAX_COSINE_DISTANCE}/data/"
    if [ ! -d "${DIR_SAVE}" ]; then
        mkdir -p ${DIR_SAVE}
    fi

    CMD="${BASE_CMD} LiteSORT --dir_save ${DIR_SAVE} --input_resolution ${INPUT_RESOLUTION} --min_confidence ${MIN_CONFIDENCE} --appearance_feature_layer ${APPEARANCE_LAYER} --max_cosine_distance ${MAX_COSINE_DISTANCE} --appearance_only_matching "
    echo "Executing command: ${CMD}"
    eval ${CMD}

    echo "Experiment completed for ${TRACKER_NAME} with Appearance Layer ${APPEARANCE_LAYER} and Max Cosine Distance ${MAX_COSINE_DISTANCE}!"
}

# Iterate over specific resolutions, confidence thresholds, appearance layers, and max cosine distances
for INPUT_RESOLUTION in 1280; do
    for MIN_CONFIDENCE in .25; do
        for LAYER in 0 1 3 5 7; do
            for MAX_COSINE_DISTANCE in 0.1 0.15 0.2 0.25 0.3; do  # Iterate over desired cosine distances
                APPEARANCE_LAYER="layer${LAYER}"
                run_tracker ${INPUT_RESOLUTION} ${MIN_CONFIDENCE} ${APPEARANCE_LAYER} ${MAX_COSINE_DISTANCE}
            done
        done
    done
done
