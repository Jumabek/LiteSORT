import cv2
import glob

# Pattern to match the video files
video_pattern = 'results/scenarios/KITTI-train-person-fps/*/data/0000.avi'

# Get all video paths that match the pattern
video_paths = glob.glob(video_pattern)

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
# Using 'mp4v' codec
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

frame_width = int(caps[0].get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(caps[0].get(cv2.CAP_PROP_FRAME_HEIGHT))

# Setup the output video writer with resolution adjusted for 4 rows and 1 column
out = cv2.VideoWriter('results/scenarios/KITTI-train-person-fps/0000_output.mp4', fourcc, 30.0,
                      (frame_width, frame_height * 4))  # Width stays the same, height is multiplied by 4

while True:
    # Read a frame from each video
    frames = [cap.read()[1] for cap in caps]

    # Check if any frame is None
    if any(frame is None for frame in frames):
        break

    # Resize frames to a common size (optional, ensure this matches the expected input for VideoWriter)
    # Here it's assumed all frames are already of correct size, no resizing is done

    # Combine frames vertically since we want 4 rows and 1 column
    final_frame = cv2.vconcat(frames)

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
