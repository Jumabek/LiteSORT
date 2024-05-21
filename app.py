import streamlit as st
import os
import subprocess
from tempfile import NamedTemporaryFile

# Define the tracking methods
LiteSORT_TRACKING_METHODS = ['SORT', 'LiteSORT', 'StrongSORT', 'DeepSORT']
YOLO_TRACKING_METHODS = ['bytetrack', 'botsort', 'strongsort', 'ocsort', 'deepocsort', 'hybridsort']

st.title("Tracker Dashboard")

# Create a layout with two columns
col1, col2 = st.columns(2)

# Dropdown menu for choosing the LiteSORT tracking method
with col1:
    LiteSORT_tracking_method = st.selectbox(
        "Choose LiteSORT Tracking Method:",
        LiteSORT_TRACKING_METHODS
    )

# Dropdown menu for choosing the YOLO tracking method
with col2:
    YOLO_tracking_method = st.selectbox(
        "Choose YOLO Tracking Method:",
        YOLO_TRACKING_METHODS
    )

# File uploader for the video file
uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "avi", "mov"])

# Run button
if st.button("Run"):
    if uploaded_file is not None:
        # Save the uploaded video file to a temporary location
        with NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.read())
            temp_filename = temp_file.name

        # Save the uploaded video as .mp4 format
        file_path = '/content/LiteSORT/uploaded_video.mp4'  # Save as .mp4
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getvalue())

        ############
        # LiteSORT #
        ############

        st.write(f"Running {LiteSORT_tracking_method} tracking on the video...")

        # Run the LiteSORT tracking command asynchronously
        lite_command = f'python UI_demo.py MOT17 train {LiteSORT_tracking_method} --input_resolution 1280 --min_confidence .25 --dir_save temp'
        #lite_command = f'python strong_sort.py {DATASET} train {LiteSORT_tracking_method} --dir_save temp --input_resolution 1280 --min_confidence .25'
        lite_process = subprocess.Popen(lite_command.split())

        ############
        # YOLOSORT #
        ############

        st.write(f"Running {YOLO_tracking_method} tracking on the video...")

        # Run the YOLOSORT tracking command asynchronously
        yolo_command = f'python /content/yolo_tracking/tracking/track.py --tracking-method {YOLO_tracking_method} --source {file_path} --save --project /content --name processed_video --exist-ok'
        yolo_process = subprocess.Popen(yolo_command.split())

        st.write("Processing started.")

        # Wait for both processes to finish
        lite_process.wait()
        yolo_process.wait()

        # Convert the processed video from .avi to .mp4 for LiteSORT
        os.system('ffmpeg -y -i /content/LiteSORT/output_video.avi /content/LiteSORT/output_video.mp4')

        # Convert the processed video from .avi to .mp4 for YOLOSORT
        os.system('ffmpeg -y -i /content/processed_video/uploaded_video.avi /content/processed_video/processed_video.mp4')

        st.write("Processing completed.")

    else:
        st.write("Please upload a video file.")

    # LiteSORT Path to the processed video
    processed_video_path_LiteSORT = '/content/LiteSORT/output_video.mp4'

    # YOLOSORT Path to the processed video
    processed_video_path_YOLOSORT = '/content/processed_video/processed_video.mp4'

    # Display the processed videos side by side
    if os.path.exists(processed_video_path_LiteSORT) and os.path.exists(processed_video_path_YOLOSORT):
        st.title("Processed Videos")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("LiteSORT Processed Video Player")
            video_bytes_lite = open(processed_video_path_LiteSORT, 'rb').read()
            st.video(video_bytes_lite, start_time=0, autoplay=True, loop=True)

        with col2:
            st.subheader("YOLO Processed Video Player")
            video_bytes_yolo = open(processed_video_path_YOLOSORT, 'rb').read()
            st.video(video_bytes_yolo, start_time=0, autoplay=True, loop=True)


    else:
        if not os.path.exists(processed_video_path_LiteSORT):
            st.write("LiteSORT Processed video not found. Please run the tracking first.")
        if not os.path.exists(processed_video_path_YOLOSORT):
            st.write("YOLO Processed video not found. Please run the tracking first.")
