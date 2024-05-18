#!/bin/bash

# Hardcoded Variables
EXPERIMENT_NAME="scenarios"
DATASET="PersonPath22"
SPLIT="test"

# Base Command
BASE_CMD="python3 strong_sort.py ${DATASET} ${SPLIT}"

# Function to run LiteSORT tracker with layer specification
run_tracker() {
    TRACKER_NAME="LiteSORT"
    INPUT_RESOLUTION=$1
    MIN_CONFIDENCE=$2
    APPEARANCE_LAYER=$3
    MAX_COSINE_DISTANCE=$4
    GPU_ID=$5  # New argument for specifying GPU ID

    echo "-----------------------------------"
    echo "Running tracker on GPU-${GPU_ID}: ${TRACKER_NAME} with Input Resolution: ${INPUT_RESOLUTION}, Confidence Threshold: ${MIN_CONFIDENCE}, Appearance Feature Layer: ${APPEARANCE_LAYER}, Max Cosine Distance: ${MAX_COSINE_DISTANCE}"

    DIR_SAVE="results/${EXPERIMENT_NAME}/${DATASET}/person_path_22-${SPLIT}/ReID_ONLY_${TRACKER_NAME}_${APPEARANCE_LAYER}__input_${INPUT_RESOLUTION}__conf_${MIN_CONFIDENCE}__cosdist_${MAX_COSINE_DISTANCE}/data"
    if [ ! -d "${DIR_SAVE}" ]; then
        mkdir -p ${DIR_SAVE}
    fi

    CMD="CUDA_VISIBLE_DEVICES=${GPU_ID} ${BASE_CMD} LiteSORT --dir_save ${DIR_SAVE} --input_resolution ${INPUT_RESOLUTION} --min_confidence ${MIN_CONFIDENCE} --appearance_feature_layer ${APPEARANCE_LAYER} --max_cosine_distance ${MAX_COSINE_DISTANCE}"
    echo "Executing command: ${CMD}"
    eval ${CMD} &
}

# Ensure to wait for all processes to complete
wait_all() {
    wait
    echo "All experiments completed."
}

# Main experiment loop
GPU_COUNTER=0
for INPUT_RESOLUTION in 1280; do
    for MIN_CONFIDENCE in .25; do
        for LAYER in 0 ; do
            for MAX_COSINE_DISTANCE in 0.1 0.15 0.2 0.25 0.3; do
                run_tracker ${INPUT_RESOLUTION} ${MIN_CONFIDENCE} "layer${LAYER}" ${MAX_COSINE_DISTANCE} ${GPU_COUNTER}
                GPU_COUNTER=$(( (GPU_COUNTER + 1) % 4 ))  # Cycle through GPUs 0, 1, 2, 3
            done
        done
    done
done

wait_all
