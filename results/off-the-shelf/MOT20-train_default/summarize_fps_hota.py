import os
import csv

# Define the base directories containing the tracker folders
base_dir_hota = '/workspace/LiteSORT/results/off-the-shelf/MOT20-train'
base_dir_fps = '/workspace/LiteSORT/results/fps/MOT20'

# Define the tracker folders you want to process
trackers_hota = [
    'BoTSORT__input_1280__conf_.25',
    'ByteTrack__input_1280__conf_.25',
    'DeepOC-SORT__input_1280__conf_.25',
    'OCSORT__input_1280__conf_.25'
]

trackers_fps = [
    'botsort__input_1280__conf_.25',
    'bytetrack__input_1280__conf_.25',
    'deepocsort__input_1280__conf_.25',
    'ocsort__input_1280__conf_.25'
]

# Initialize dictionaries to store HOTA scores and FPS values
hota_scores = {}
fps_values = {}

# Function to read the HOTA score from a pedestrian_summary.txt file
def get_hota_score(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        if len(lines) > 1:
            scores = lines[1].split()
            return float(scores[0])  # HOTA score is the first value on the second line

# Function to read the FPS value from a time_log.txt file
def get_fps_value(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if 'FPS:' in line:
                fps_value = line.split('FPS:')[1].strip()
                return float(fps_value)

# Function to format the tracker name
def format_tracker_name(tracker_name):
    formatted_name = tracker_name.split('__')[0].lower()
    if 'botsort' in formatted_name:
        return 'Botsort'
    elif 'bytetrack' in formatted_name:
        return 'Bytetrack'
    elif 'deepocsort' in formatted_name:
        return 'Deepoc-sort'
    elif 'ocsort' in formatted_name:
        return 'Ocsort'
    else:
        return formatted_name.capitalize()

# Loop through each tracker folder and extract the HOTA score
for tracker in trackers_hota:
    file_path = os.path.join(base_dir_hota, tracker, 'pedestrian_summary.txt')
    if os.path.exists(file_path):
        hota_scores[format_tracker_name(tracker)] = get_hota_score(file_path)

# Loop through each tracker folder and extract the FPS value
for tracker in trackers_fps:
    file_path = os.path.join(base_dir_fps, tracker, 'time_log.txt')
    if os.path.exists(file_path):
        fps_values[format_tracker_name(tracker)] = get_fps_value(file_path)

# Write the HOTA scores and FPS values to a CSV file
output_file = '/workspace/LiteSORT/results/off-the-shelf/MOT20-train/pedestrian_fps_summary.csv'
with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Tracker', ' HOTA', ' FPS'])
    for tracker in hota_scores:
        hota = hota_scores.get(tracker, 'N/A')
        fps = fps_values.get(tracker, 'N/A')
        writer.writerow([tracker, f' {hota}', f' {fps}'])

print(f'HOTA scores and FPS values have been written to {output_file}')
