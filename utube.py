import cv2
import pytube


def stream_youtube_video(url):
    yt = pytube.YouTube(url)
    video = yt.streams.filter(file_extension='mp4', resolution='360p').first()
    video_url = video.url

    cap = cv2.VideoCapture(video_url)

    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow('YouTube Video Stream', frame)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    stream_youtube_video("https://www.youtube.com/watch?v=Wyd9cYmLZ10")
