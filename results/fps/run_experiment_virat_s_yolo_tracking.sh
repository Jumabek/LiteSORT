#!/bin/bash

# Ensure bc is installed
if ! command -v bc &> /dev/null
then
    echo "bc could not be found. Installing bc..."
    sudo apt-get update
    sudo apt-get install -y bc
fi

# Hardcoded Variables
EXPERIMENT_NAME="fps"
INPUT_RESOLUTION="1280"
MIN_CONFIDENCE=".25"
DATASET="VIRAT-S"
# PATH_TO_SEQ="/workspace/LiteSORT/datasets/VIRAT-S/train/VIRAT_S_010000_06_000728_000762/img1"
PATH_TO_SEQ="/media/hbai/data/code/LiteSORT/datasets/VIRAT-S/train/VIRAT_S_010000_06_000728_000762/img1"

TOTAL_FRAMES=766  # Adjust this according to your dataset

# Base Command
# BASE_CMD="python /workspace/LiteSORT/yolo_tracking/tracking/track.py --classes 0 --yolo-model yolov8m"
BASE_CMD="python3 /media/hbai/data/code/LiteSORT/yolo_tracking/tracking/track.py --classes 0 --yolo-model yolov8m"


# Function to run tracker
run_tracker() {
    TRACKER_NAME=$1
    echo "-----------------------------------"
    echo "Running tracker: ${TRACKER_NAME}"  # Debug message

    DIR_SAVE="results/${EXPERIMENT_NAME}/${DATASET}/${TRACKER_NAME}__input_${INPUT_RESOLUTION}__conf_${MIN_CONFIDENCE}"
    mkdir -p "${DIR_SAVE}"

    CMD_OPTIONS="--project ${DIR_SAVE} --imgsz ${INPUT_RESOLUTION} --conf ${MIN_CONFIDENCE} --source ${PATH_TO_SEQ}"
    
    case ${TRACKER_NAME} in
        "deepocsort")
            
            TIME_OUTPUT=$( { time -p ${BASE_CMD} --tracking-method deepocsort ${CMD_OPTIONS}; } 2>&1 )
            ;;
        "botsort")
            
            TIME_OUTPUT=$( { time -p ${BASE_CMD} --tracking-method botsort ${CMD_OPTIONS}; } 2>&1 )
            ;;
        "ocsort")
            
            TIME_OUTPUT=$( { time -p ${BASE_CMD} --tracking-method ocsort ${CMD_OPTIONS}; } 2>&1 )
            ;;
        "bytetrack")
            
            TIME_OUTPUT=$( { time -p ${BASE_CMD} --tracking-method bytetrack ${CMD_OPTIONS}; } 2>&1 )
            ;;
        *)
            echo "Invalid tracker name"
            exit 1
            ;;
    esac
    
    echo "${TIME_OUTPUT}" | tee "${DIR_SAVE}/time_log.txt"

    # Parse real time using time -p
    REAL_TIME=$(echo "${TIME_OUTPUT}" | grep real | awk '{print $2}')
    echo "Parsed real time: ${REAL_TIME} seconds"  # Debug message

    if (( $(echo "$REAL_TIME == 0" | bc -l) )); then
        echo "Total time is zero, cannot calculate FPS."
    else
        FPS=$(echo "scale=2; ${TOTAL_FRAMES} / ${REAL_TIME}" | bc -l)
        echo "FPS: ${FPS}" | tee -a "${DIR_SAVE}/time_log.txt"
    fi

    echo "Experiment completed for ${TRACKER_NAME}!"
}

# List of trackers
TRACKERS=('deepocsort' 'bytetrack' 'ocsort' 'botsort')
# Run experiments for all trackers
for TRACKER in "${TRACKERS[@]}"; do
    run_tracker "${TRACKER}"
done
