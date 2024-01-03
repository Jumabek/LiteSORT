#!/bin/bash

# Hardcoded Variables
EXPERIMENT_NAME="off-the-shelf"
INPUT_RESOLUTION="1280"
MIN_CONFIDENCE=".25"
DATASET="MOT17"

# Base Command
BASE_CMD="python strong_sort.py ${DATASET} train"

# Function to run tracker
run_tracker() {

    TRACKER_NAME=$1
    echo "-----------------------------------"
    echo "Running tracker: ${TRACKER_NAME}"  # Debug message


    DIR_SAVE="results/${EXPERIMENT_NAME}/${DATASET}/${TRACKER_NAME}__input_${INPUT_RESOLUTION}__conf_${MIN_CONFIDENCE}"
    if [ ! -d "${DIR_SAVE}" ]; then
        mkdir -p ${DIR_SAVE}
    fi

    case ${TRACKER_NAME} in
        "SORT")
            ${BASE_CMD} --iou_only --dir_save ${DIR_SAVE} --input_resolution ${INPUT_RESOLUTION} --min_confidence ${MIN_CONFIDENCE}
            ;;
        "LiteSORT")
            ${BASE_CMD} --yolosort --dir_save ${DIR_SAVE} --input_resolution ${INPUT_RESOLUTION} --min_confidence ${MIN_CONFIDENCE}
            ;;
        "DeepSORT")
            ${BASE_CMD} --dir_save ${DIR_SAVE} --input_resolution ${INPUT_RESOLUTION} --min_confidence ${MIN_CONFIDENCE}
            ;;
        "StrongSORT")
            ${BASE_CMD} --dir_save ${DIR_SAVE} --input_resolution ${INPUT_RESOLUTION} --min_confidence ${MIN_CONFIDENCE} --BoT --ECC --NSA --EMA --MC --woC
            ;;
        *)
            echo "Invalid tracker name"
            exit 1
            ;;
    esac
    echo "Experiment completed for ${TRACKER_NAME}!"
}

# Run experiments for all trackers
# run_tracker "SORT"
run_tracker "LiteSORT"
# run_tracker "DeepSORT"
run_tracker "StrongSORT"
