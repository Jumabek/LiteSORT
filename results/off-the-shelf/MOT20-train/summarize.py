import os
import csv

# Define the base directory containing the tracker folders
base_dir = '/workspace/LiteSORT/results/off-the-shelf/MOT20-train'

# Define the tracker folders you want to process
trackers = [
    'BoTSORT__input_1280__conf_.25',
    'ByteTrack__input_1280__conf_.25',
    'DeepOC-SORT__input_1280__conf_.25',
    'OCSORT__input_1280__conf_.25'
]

# Initialize a dictionary to store HOTA scores
hota_scores = {}

# Function to read the HOTA score from a pedestrian_summary.txt file
def get_hota_score(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        if len(lines) > 1:
            scores = lines[1].split()
            return float(scores[0])  # HOTA score is the first value on the second line

# Function to format the tracker name
def format_tracker_name(tracker_name):
    return tracker_name.split('__')[0]

# Loop through each tracker folder and extract the HOTA score
for tracker in trackers:
    file_path = os.path.join(base_dir, tracker, 'pedestrian_summary.txt')
    if os.path.exists(file_path):
        hota_scores[format_tracker_name(tracker)] = get_hota_score(file_path)

# Write the HOTA scores to a CSV file with spaces between columns
output_file = '/workspace/LiteSORT/results/off-the-shelf/MOT20-train/pedestrian_summary.csv'
with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Tracker', ' HOTA'])
    for tracker, score in hota_scores.items():
        writer.writerow([tracker, f' {score}'])

print(f'HOTA scores have been written to {output_file}')
