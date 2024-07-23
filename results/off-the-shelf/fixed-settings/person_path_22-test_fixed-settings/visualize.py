import os
import cv2
import argparse

def draw_bounding_boxes(image_dir, result_file, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(result_file, 'r') as file:
        lines = file.readlines()
    
    bbox_data = {}
    for line in lines:
        data = line.strip().split(',')
        frame_id = int(data[0])
        track_id = int(data[1])
        x, y, w, h = map(float, data[2:6])
        
        if frame_id not in bbox_data:
            bbox_data[frame_id] = []
        
        bbox_data[frame_id].append((track_id, x, y, w, h))
    
    frame_paths = []
    for frame_id in sorted(bbox_data.keys()):
        image_path = os.path.join(image_dir, f"{(frame_id-1):06d}.jpg")
        image = cv2.imread(image_path)
        
        for bbox in bbox_data[frame_id]:
            track_id, x, y, w, h = bbox
            top_left = (int(x), int(y))
            bottom_right = (int(x + w), int(y + h))
            cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
            cv2.putText(image, str(track_id), (int(x), int(y) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        output_image_path = os.path.join(output_dir, f"{(frame_id-1):06d}.jpg")
        cv2.imwrite(output_image_path, image)
        frame_paths.append(output_image_path)
        print(f"Processed frame {frame_id-1}")
    
    return frame_paths

def create_video_from_frames(frame_paths, video_output_path, fps=30):
    if not frame_paths:
        print("No frames to create a video.")
        return
    
    # Read the first frame to get the dimensions
    frame = cv2.imread(frame_paths[0])
    height, width, layers = frame.shape

    # Initialize the video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(video_output_path, fourcc, fps, (width, height))

    for frame_path in frame_paths:
        frame = cv2.imread(frame_path)
        video.write(frame)

    video.release()
    print(f"Video saved at {video_output_path}")

def main(tracking_method, sequence):
    # Define the mapping from tracking method to directory names
    tracking_dirs = {
        'bytetrack': 'ByteTRACK__input_1280__conf_.25',
        'botsort': 'BoTSORT__input_1280__conf_.25',
        'deepocsort': 'DeepOC-SORT__input_1280__conf_.25',
        'ocsort': 'OCSORT__input_1280__conf_.25'
    }
    
    if tracking_method.lower() not in tracking_dirs:
        print(f"Unknown tracking method: {tracking_method}")
        return
    
    tracking_dir = tracking_dirs[tracking_method.lower()]
    image_dir = f'/media/hbai/data/code/LiteSORT/datasets/PersonPath22/test/{sequence}/img1'
    result_file = f'/media/hbai/data/code/LiteSORT/results/off-the-shelf/fixed-settings/person_path_22-test_fixed-settings/{tracking_dir}/data/{sequence}.txt'
    output_dir = f'/media/hbai/data/code/LiteSORT/results/off-the-shelf/fixed-settings/person_path_22-test_fixed-settings/{sequence}/{tracking_dir}'
    video_output_path = f'{output_dir}_{tracking_method}.mp4'

    frame_paths = draw_bounding_boxes(image_dir, result_file, output_dir)
    create_video_from_frames(frame_paths, video_output_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Visualize tracking results and create a video.')
    parser.add_argument('--tracking-method', type=str, required=True, help='Tracking method to use (e.g., bytetrack, botsort)')
    parser.add_argument('--sequence', type=str, required=True, help='Sequence name (e.g., uid_vid_00126.mp4)')

    args = parser.parse_args()
    main(args.tracking_method, args.sequence)
