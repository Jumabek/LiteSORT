#!/bin/bash

# Hardcoded Variables
EXPERIMENT_NAME="off-the-shelf"
INPUT_RESOLUTION="1280"
MIN_CONFIDENCE=".25"
DATASET="DanceTrack"

# Base Command
BASE_CMD="python3 strong_sort.py ${DATASET} train"

# Function to run tracker
run_tracker() {
    TRACKER_NAME=$1
    echo "-----------------------------------"
    echo "Running tracker: ${TRACKER_NAME}"  # Debug message

    DIR_SAVE="results/${EXPERIMENT_NAME}/${DATASET}_Simple_trackers/${TRACKER_NAME}__input_${INPUT_RESOLUTION}__conf_${MIN_CONFIDENCE}"
    mkdir -p "${DIR_SAVE}"

    CMD_OPTIONS="--dir_save ${DIR_SAVE} --input_resolution ${INPUT_RESOLUTION} --min_confidence ${MIN_CONFIDENCE}"

    case ${TRACKER_NAME} in
        "SORT")
            ${BASE_CMD} "SORT" ${CMD_OPTIONS} 
            ;;
        "LiteSORT")
            ${BASE_CMD} "LiteSORT" ${CMD_OPTIONS} --woC --appearance_feature_layer "layer0"
            ;;
        "DeepSORT")
            ${BASE_CMD} "DeepSORT" ${CMD_OPTIONS}
            ;;
        "StrongSORT")
            ${BASE_CMD} "StrongSORT" ${CMD_OPTIONS} --BoT --ECC --NSA --EMA --MC --woC
            ;;
        *)
            echo "Invalid tracker name"
            exit 1
            ;;
    esac
    echo "Experiment completed for ${TRACKER_NAME}!"
}

# List of trackers
TRACKERS=("SORT" "LiteSORT" "DeepSORT" "StrongSORT")

# Run experiments for all trackers
for TRACKER in "${TRACKERS[@]}"; do
    run_tracker "${TRACKER}"
done
