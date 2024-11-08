#!/bin/bash


# Hardcoded Variables
EXPERIMENT_NAME="scenarios"
DATASET="VIRAT-S"

# Base Command
BASE_CMD="python strong_sort_fps.py ${DATASET} train "


# Function to run tracker
run_tracker() {

    TRACKER_NAME=$1
    echo "-----------------------------------"
    echo "Running tracker: ${TRACKER_NAME} with Input Resolution: ${INPUT_RESOLUTION} and Confidence Threshold: ${MIN_CONFIDENCE}"  # Debug message

    DIR_SAVE="results/${EXPERIMENT_NAME}/${DATASET}-train-fps/${TRACKER_NAME}__input_${INPUT_RESOLUTION}__conf_${MIN_CONFIDENCE}/data/"
    if [ ! -d "${DIR_SAVE}" ]; then
        mkdir -p ${DIR_SAVE}
    fi

    case ${TRACKER_NAME} in
        "SORT")
            ${BASE_CMD} SORT --dir_save ${DIR_SAVE} --input_resolution ${INPUT_RESOLUTION} --min_confidence ${MIN_CONFIDENCE}
            ;;
        "LiteSORT")
            CMD="${BASE_CMD} LiteSORT --dir_save ${DIR_SAVE} --input_resolution ${INPUT_RESOLUTION} --min_confidence ${MIN_CONFIDENCE} --appearance_feature_layer layer0"
            echo "Executing command: ${CMD}"
            eval ${CMD}
            ;;
        "DeepSORT")
            ${BASE_CMD} DeepSORT --dir_save ${DIR_SAVE} --input_resolution ${INPUT_RESOLUTION} --min_confidence ${MIN_CONFIDENCE}
            ;;
        "StrongSORT")
            ${BASE_CMD} StrongSORT  --EMA --dir_save ${DIR_SAVE} --input_resolution ${INPUT_RESOLUTION} --min_confidence ${MIN_CONFIDENCE} --BoT --ECC --NSA --EMA --MC --woC
            ;;
        *)
            echo "Invalid tracker name"
            exit 1
            ;;
    esac
    echo "Experiment completed for ${TRACKER_NAME}!"
}

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
