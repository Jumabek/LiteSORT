#!/bin/bash

# Hardcoded Variables
EXPERIMENT_NAME="scenarios"
DATASET="PersonPath22"
SPLIT="test"

# Base Command
BASE_CMD="python3 strong_sort_single_process.py ${DATASET} ${SPLIT}"

# Function to run LiteSORT tracker with layer specification
run_tracker() {
    TRACKER_NAME="LiteSORT"
    INPUT_RESOLUTION=$1
    MIN_CONFIDENCE=$2
    APPEARANCE_LAYER=$3
    MAX_COSINE_DISTANCE=$4
    MAX_AGE=$5

    echo "-----------------------------------"
    echo "Running tracker: ${TRACKER_NAME} with Input Resolution: ${INPUT_RESOLUTION}, Confidence Threshold: ${MIN_CONFIDENCE}, Appearance Feature Layer: ${APPEARANCE_LAYER}, Max Cosine Distance: ${MAX_COSINE_DISTANCE}, Max Age: ${MAX_AGE}"

    DIR_SAVE="results/${EXPERIMENT_NAME}/${DATASET}/person_path_22-${SPLIT}/visualization_${APPEARANCE_LAYER}__cosdist_${MAX_COSINE_DISTANCE}__maxage_${MAX_AGE}/data"
    if [ ! -d "${DIR_SAVE}" ]; then
        mkdir -p ${DIR_SAVE}
    fi

    CMD="${BASE_CMD} LiteSORT --dir_save ${DIR_SAVE} --input_resolution ${INPUT_RESOLUTION} --min_confidence ${MIN_CONFIDENCE} --appearance_feature_layer ${APPEARANCE_LAYER} --max_cosine_distance ${MAX_COSINE_DISTANCE} --max_age ${MAX_AGE}"
    echo "Executing command: ${CMD}"
    eval ${CMD}
    echo "Experiment completed for ${TRACKER_NAME} with Appearance Layer: ${APPEARANCE_LAYER}, Max Cosine Distance: ${MAX_COSINE_DISTANCE}, and Max Age: ${MAX_AGE}!"
}

# Iterate over specific resolutions, confidence thresholds, appearance layers, max cosine distances, and max ages
for INPUT_RESOLUTION in 1280; do
    for MIN_CONFIDENCE in .25; do
        for LAYER in 3; do
            for MAX_COSINE_DISTANCE in  0.3 ; do  # Iterate over desired cosine distances
                for MAX_AGE in 30; do
                    APPEARANCE_LAYER="layer${LAYER}"
                    run_tracker ${INPUT_RESOLUTION} ${MIN_CONFIDENCE} ${APPEARANCE_LAYER} ${MAX_COSINE_DISTANCE} ${MAX_AGE}
                done
            done
        done
    done
done
