#!/bin/bash

# Hardcoded Variables
EXPERIMENT_NAME="scenarios"
DATASET="KITTI"
SPLIT="train"
CLASSES="2 5 7"  # Classes for vehicle detection

# Base Command
BASE_CMD="python3 strong_sort.py ${DATASET} ${SPLIT}"

# Function to run tracker
run_tracker() {
    TRACKER_NAME=$1
    echo "-----------------------------------"
    echo "Running tracker: ${TRACKER_NAME} with Input Resolution: ${INPUT_RESOLUTION} and Confidence Threshold: ${MIN_CONFIDENCE}"  # Debug message

    DIR_SAVE="results/${EXPERIMENT_NAME}/${DATASET}-${SPLIT}/${TRACKER_NAME}__input_${INPUT_RESOLUTION}__conf_${MIN_CONFIDENCE}/data"
    if [ ! -d "${DIR_SAVE}" ]; then
        mkdir -p "${DIR_SAVE}"
    fi

    case ${TRACKER_NAME} in
        "SORT")
            CMD="${BASE_CMD} SORT --classes ${CLASSES} --dir_save ${DIR_SAVE} --input_resolution ${INPUT_RESOLUTION} --min_confidence ${MIN_CONFIDENCE}"
            ;;
        "LiteSORT")
            CMD="${BASE_CMD} LiteSORT --classes ${CLASSES} --dir_save ${DIR_SAVE} --input_resolution ${INPUT_RESOLUTION} --min_confidence ${MIN_CONFIDENCE} --appearance_feature_layer layer0"
            ;;
        "DeepSORT")
            CMD="${BASE_CMD} DeepSORT --classes ${CLASSES} --dir_save ${DIR_SAVE} --input_resolution ${INPUT_RESOLUTION} --min_confidence ${MIN_CONFIDENCE}"
            ;;
        "StrongSORT")
            CMD="${BASE_CMD} StrongSORT --classes ${CLASSES} --dir_save ${DIR_SAVE} --input_resolution ${INPUT_RESOLUTION} --min_confidence ${MIN_CONFIDENCE} --BoT --NSA --EMA --MC --woC"
            ;;
        *)
            echo "Invalid tracker name"
            exit 1
            ;;
    esac

    echo "Executing command: ${CMD}"
    eval "${CMD}"
    if [ $? -eq 0 ]; then
        echo "Experiment completed for ${TRACKER_NAME}!"
    else
        echo "Experiment failed for ${TRACKER_NAME}."
    fi
}

# Check if Python command exists
if ! command -v python3 &> /dev/null; then
    echo "python3 could not be found, please install Python."
    exit 1
fi

# Iterate over multiple resolutions and confidence thresholds
for INPUT_RESOLUTION in 1280; do
    for MIN_CONFIDENCE in .25; do
        # Run experiments for all trackers
        run_tracker "SORT"
        run_tracker "LiteSORT"
        run_tracker "DeepSORT"
        run_tracker "StrongSORT"
    done
done

wait
