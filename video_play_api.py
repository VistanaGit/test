from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import cv2
import os

app = FastAPI()

# Set the directory where video files are stored
VIDEO_DIRECTORY = "Videos/"  # Path to the Videos directory

@app.get("/video/{filename}")
def stream_video(filename: str):
    # Allowed video extensions
    allowed_extensions = [".mp4", ".avi"]

    # Ensure the file has an allowed extension
    if not any(filename.endswith(ext) for ext in allowed_extensions):
        return {"error": "Invalid file extension. Only .mp4 and .avi are allowed."}

    # Construct the full video file path
    video_path = os.path.join(VIDEO_DIRECTORY, filename)

    # Check if the file exists
    if not os.path.isfile(video_path):
        return {"error": "File not found"}

    # Open the video using OpenCV
    video_capture = cv2.VideoCapture(video_path)

    # Check if the video can be opened
    if not video_capture.isOpened():
        return {"error": "Unable to open video file"}

    # Generator function to stream video frames
    def generate_video_stream():
        while video_capture.isOpened():
            success, frame = video_capture.read()
            if not success:
                break

            # Convert the frame to JPG format
            _, buffer = cv2.imencode('.jpg', frame)

            # Yield the frame as a byte sequence
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n\r\n')

    # Return streaming response with multipart data
    return StreamingResponse(generate_video_stream(), media_type="multipart/x-mixed-replace; boundary=frame")
