from fastapi import FastAPI, Response
import cv2

app = FastAPI()

@app.get("/Videos/{filename}")
def stream_video(filename: str):
    # Assuming NVR path is where the video files are stored
    video_path = f"/path_to_nvr/{filename}"

    # OpenCV to read video frames
    video_capture = cv2.VideoCapture(video_path)

    def generate_video_stream():
        while video_capture.isOpened():
            success, frame = video_capture.read()
            if not success:
                break

            # Convert frame to JPG and yield as streaming data
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    return Response(generate_video_stream(), media_type="multipart/x-mixed-replace; boundary=frame")
