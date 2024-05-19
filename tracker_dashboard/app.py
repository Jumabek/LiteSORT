import streamlit as st
import os
from tempfile import NamedTemporaryFile

# Define the tracking methods
TRACKING_METHODS = ['SORT', 'LiteSORT', 'StrongSORT', 'DeepSORT']

st.title("YOLO Tracking Method Selector")

# Dropdown menu for choosing the tracking method
tracking_method = st.selectbox(
    "Choose Tracking Method:",
    TRACKING_METHODS
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

        st.write(f"Running {tracking_method} tracking on the video...")

        # Save the uploaded video as .mp4 format
        file_path = '/content/LiteSORT/uploaded_video.mp4'  # Save as .mp4
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getvalue())

        # Run the tracking command
        # python lite_sort_demo.py MOT17 train SORT --input_resolution 1280 --min_confidence .25 --dir_save temp
        command = f'python lite_sort_demo.py MOT17 train {tracking_method} --input_resolution 1280 --min_confidence .25 --dir_save temp'
        os.system(command)

        # Convert the processed video from .avi to .mp4
        os.system('ffmpeg -y -i /content/LiteSORT/output_video.avi /content/LiteSORT/output_video.mp4')

        st.write("Processing completed.")
    else:
        st.write("Please upload a video file.")

    # Path to the processed video
    processed_video_path = '/content/LiteSORT/output_video.mp4'

    # Display the processed video
    if os.path.exists(processed_video_path):
        st.title("Processed Video Player")
        with open(processed_video_path, 'rb') as video_file:
            video_bytes = video_file.read()
        st.video(video_bytes)
    else:
        st.write("Processed video not found. Please run the tracking first.")
