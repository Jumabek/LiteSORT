python scripts/run_mot_challenge.py \
--BENCHMARK MOT17 \
--SPLIT_TO_EVAL train \
--TRACKERS_TO_EVAL /home/juma/code/StrongSORT/results/StrongSORT_Git/tmp \
--TRACKER_SUB_FOLDER '' \
--METRICS HOTA CLEAR  Identity VACE  \
--USE_PARALLEL False \
--NUM_PARALLEL_CORES 1 \
--GT_LOC_FORMAT '{gt_folder}/{seq}/gt/gt.txt' \
--OUTPUT_SUMMARY True \
--OUTPUT_EMPTY_CLASSES False \
--OUTPUT_DETAILED False \
--PLOT_CURVES False