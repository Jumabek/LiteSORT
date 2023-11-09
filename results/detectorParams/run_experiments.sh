#!/bin/bash


# Hardcoded Variables
EXPERIMENT_NAME="detectorParams"
DATASET="MOT17"

# Base Command
BASE_CMD="python strong_sort.py ${DATASET} val"

# Function to run tracker
run_tracker() {

    TRACKER_NAME=$1
    echo "-----------------------------------"
    echo "Running tracker: ${TRACKER_NAME} with Input Resolution: ${INPUT_RESOLUTION} and Confidence Threshold: ${MIN_CONFIDENCE}"  # Debug message

    DIR_SAVE="results/${EXPERIMENT_NAME}/${TRACKER_NAME}__input_${INPUT_RESOLUTION}__conf_${MIN_CONFIDENCE}"
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
        "deepSORT")
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

# Iterate over multiple resolutions and confidence thresholds
for INPUT_RESOLUTION in 320 640 960 1280 1600 1920 2240 2560; do
    for MIN_CONFIDENCE in .25 .3 .35 .4 .45 .5 .55 .6 .65 .7; do
        # Run experiments for all trackers
        run_tracker "SORT"
        run_tracker "LiteSORT"
        run_tracker "deepSORT"
        run_tracker "StrongSORT"
    done
done
