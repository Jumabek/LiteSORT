import os
import csv

# Define the base directory containing the tracker folders
base_dir = '/workspace/LiteSORT/results/fps/MOT20'

# Define the tracker folders you want to process
trackers = [
    'botsort__input_1280__conf_.25',
    'bytetrack__input_1280__conf_.25',
    'deepocsort__input_1280__conf_.25',
    'ocsort__input_1280__conf_.25'
]

# Initialize a dictionary to store FPS values
fps_values = {}

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
    return tracker_name.split('__')[0].capitalize()

# Loop through each tracker folder and extract the FPS value
for tracker in trackers:
    file_path = os.path.join(base_dir, tracker, 'time_log.txt')
    if os.path.exists(file_path):
        fps_values[format_tracker_name(tracker)] = get_fps_value(file_path)

# Write the FPS values to a CSV file with spaces between columns
output_file = '/workspace/LiteSORT/results/fps/MOT20/fps_summary.csv'
with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Tracker', ' FPS'])
    for tracker, fps in fps_values.items():
        writer.writerow([tracker, f' {fps}'])

print(f'FPS values have been written to {output_file}')
