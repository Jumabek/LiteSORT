import cv2
import glob
from os.path import join

ROOT = 'results/scenarios/PersonPath22/person_path_22-test-fps'
# Pattern to match the video files
# 'results/scenarios/VIRAT-S-train-fps/{}/data/VIRAT_S_050000_10_001462_001491.avi'
video_pattern = join(ROOT, '{}/data/uid_vid_00008.mp4.avi')

# Get all video paths that match the pattern
video_paths = [
    video_pattern.format(tracker_name+'__input_1280__conf_.25_max_cosine_distance_0.5') for tracker_name in ('SORT', 'LiteSORT', 'DeepSORT', 'StrongSORT')]


# Check if we have exactly four videos, if not, handle the case
if len(video_paths) != 4:
    print("Error: Expected exactly four videos, got {}".format(len(video_paths)))
    exit(1)

# Open all video captures
caps = []
for path in video_paths:
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        print(f"Error: Cannot open the video file {path}")
        exit(1)
    caps.append(cap)

# Check if all videos are opened successfully
if not all(cap.isOpened() for cap in caps):
    print("Error opening one or more video files")
    exit(1)

# Define the codec and create VideoWriter object
# Using 'avc1' (H.264 codec) which might require additional configurations on some systems
# fourcc = cv2.VideoWriter_fourcc(*'avc1')
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

frame_width = int(caps[0].get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(caps[0].get(cv2.CAP_PROP_FRAME_HEIGHT))
outfile = join(ROOT, 'MOT20-01.mp4')

out = cv2.VideoWriter(outfile, fourcc, 30.0,
                      (frame_width * 2, frame_height * 2))

while True:
    # Read a frame from each video
    frames = [cap.read()[1] for cap in caps]

    # Check if any frame is None
    if any(frame is None for frame in frames):
        break

    # Resize frames to a common size (ensure this matches the expected input for VideoWriter)
    resized_frames = [cv2.resize(
        frame, (frame_width, frame_height)) for frame in frames]

    # Combine frames horizontally
    top_row = cv2.hconcat(resized_frames[:2])  # First two for the top row
    bottom_row = cv2.hconcat(resized_frames[2:])  # Last two for the bottom row

    # Combine top and bottom rows vertically
    final_frame = cv2.vconcat([top_row, bottom_row])

    # Write the frame into the file 'output.mp4'
    out.write(final_frame)

    # Optionally, display the frame (for testing purposes)
    cv2.imshow('Frame', final_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release everything when done
for cap in caps:
    cap.release()
out.release()
cv2.destroyAllWindows()
