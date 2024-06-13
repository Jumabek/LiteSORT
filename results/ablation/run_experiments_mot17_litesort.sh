#!/bin/bash

# Hardcoded Variables
EXPERIMENT_NAME="scenarios"
DATASET="MOT17"
SPLIT="train"

# Base Command
BASE_CMD="python3 strong_sort.py ${DATASET} ${SPLIT}"

# Function to run LiteSORT tracker with layer specification
run_tracker() {
    TRACKER_NAME="LiteSORT"
    INPUT_RESOLUTION=$1
    MIN_CONFIDENCE=$2
    APPEARANCE_LAYER=$3
    MAX_COSINE_DISTANCE=$4
    APPEARANCE_ONLY_FLAG=$5
    MAX_AGE=$6

    echo "-----------------------------------"
    echo "Running tracker: ${TRACKER_NAME} with Input Resolution: ${INPUT_RESOLUTION}, Confidence Threshold: ${MIN_CONFIDENCE}, Appearance Feature Layer: ${APPEARANCE_LAYER}, Max Cosine Distance: ${MAX_COSINE_DISTANCE}, Appearance Only: ${APPEARANCE_ONLY_FLAG}, Max Age: ${MAX_AGE}"

    DIR_SAVE="results/${EXPERIMENT_NAME}/${DATASET}-${SPLIT}/${APPEARANCE_LAYER}_${TRACKER_NAME}__input_${INPUT_RESOLUTION}__conf_${MIN_CONFIDENCE}__cosdist_${MAX_COSINE_DISTANCE}__maxage_${MAX_AGE}/data/"
    if [ ! -d "${DIR_SAVE}" ]; then
        mkdir -p "${DIR_SAVE}"
    fi

    # Adjust command based on appearance only flag
    if [ "${APPEARANCE_ONLY_FLAG}" = "true" ]; then
        CMD="${BASE_CMD} LiteSORT --dir_save ${DIR_SAVE} --input_resolution ${INPUT_RESOLUTION} --min_confidence ${MIN_CONFIDENCE} --appearance_feature_layer ${APPEARANCE_LAYER} --max_cosine_distance ${MAX_COSINE_DISTANCE} --max_age ${MAX_AGE} --appearance_only_matching"
    else
        CMD="${BASE_CMD} LiteSORT --dir_save ${DIR_SAVE} --input_resolution ${INPUT_RESOLUTION} --min_confidence ${MIN_CONFIDENCE} --appearance_feature_layer ${APPEARANCE_LAYER} --max_cosine_distance ${MAX_COSINE_DISTANCE} --max_age ${MAX_AGE}"
    fi

    echo "Executing command: ${CMD}"
    eval "${CMD}"
    if [ $? -eq 0 ]; then
        echo "Experiment completed for ${TRACKER_NAME} with Appearance Layer: ${APPEARANCE_LAYER}, Max Cosine Distance: ${MAX_COSINE_DISTANCE}, Appearance Only: ${APPEARANCE_ONLY_FLAG}, Max Age: ${MAX_AGE}!"
    else
        echo "Experiment failed for ${TRACKER_NAME} with Appearance Layer: ${APPEARANCE_LAYER}, Max Cosine Distance: ${MAX_COSINE_DISTANCE}, Appearance Only: ${APPEARANCE_ONLY_FLAG}, Max Age: ${MAX_AGE}."
    fi
}

# Check if Python command exists
if ! command -v python3 &> /dev/null; then
    echo "python3 could not be found, please install Python."
    exit 1
fi

# Iterate over specific resolutions, confidence thresholds, appearance layers, max cosine distances, and max ages
APPEARANCE_ONLY="true"  # Set this to "true" or "false" as needed
for INPUT_RESOLUTION in 1280; do
    for MIN_CONFIDENCE in .25; do
        for LAYER in 3 5 7; do
            for MAX_COSINE_DISTANCE in 0.3; do
                for MAX_AGE in  30; do
                    APPEARANCE_LAYER="layer${LAYER}"
                    run_tracker "${INPUT_RESOLUTION}" "${MIN_CONFIDENCE}" "${APPEARANCE_LAYER}" "${MAX_COSINE_DISTANCE}" "${APPEARANCE_ONLY}" "${MAX_AGE}"
                done
            done
        done
    done
done

wait
