from fastapi import FastAPI, Response
import cv2
import os

app = FastAPI()

# Define the base path where video files are stored (NVR storage path)
NVR_STORAGE_PATH = "/path_to_nvr"  # Replace with the actual path

@app.get("/video/{filename}")
def stream_video(filename: str):
    # Safely construct the full video file path
    video_path = os.path.join(NVR_STORAGE_PATH, filename)

    # Check if the file exists
    if not os.path.isfile(video_path):
        return {"error": "File not found"}

    # Open the video using OpenCV
    video_capture = cv2.VideoCapture(video_path)

    # Generator function to stream video frames
    def generate_video_stream():
        while video_capture.isOpened():
            success, frame = video_capture.read()
            if not success:
                break

            # Convert each frame to JPEG format and yield
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    # Return streaming response
    return Response(generate_video_stream(), media_type="multipart/x-mixed-replace; boundary=frame")
