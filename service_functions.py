from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from db_initialize import Account, Camera, Counter, ROI, Visitor
from db_configure import SessionLocal 


# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Login data model for request body
class LoginData(BaseModel):
    username: str
    password: str

# Password recovery data model for request body
class PasswordRecoveryData(BaseModel):
    email: EmailStr

# Function for password recovery
def recover_password(recovery_data: PasswordRecoveryData, db: Session):
    # Query the database to find the account associated with the provided email
    account = db.query(Account).filter(Account.email == recovery_data.email).first()

    if not account:
        raise HTTPException(status_code=404, detail="Email not registered")

    # Show the retrieved password (in a real application, this might be a security risk)
    return {"message": f"Your password is: {account.password}"}

# Function to handle login
def login(login_data: LoginData, db: Session):
    # Query the database for the account with the provided username
    account = db.query(Account).filter(Account.user_name == login_data.username).first()

    if not account:
        raise HTTPException(status_code=400, detail="Username or password is wrong")

    # Check if the password matches
    if account.password != login_data.password:
        raise HTTPException(status_code=400, detail="Username or password is wrong")

    return {"message": "Successful login"}

# Function for streaming video
def stream_video(filename: str, frame_rate: int, VIDEO_DIRECTORY: str):
    import cv2
    import os
    import time
    from fastapi.responses import StreamingResponse

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

    # Calculate the delay time between frames
    frame_time = 1.0 / frame_rate  # Time between frames in seconds

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

            # Introduce a delay to control the frame rate
            time.sleep(frame_time)

    # Return streaming response with multipart data
    return StreamingResponse(generate_video_stream(), media_type="multipart/x-mixed-replace; boundary=frame")

# Function for fetching account list
def get_account_list(db: Session):
    return db.query(Account).all()

# Function for fetching camera list
def get_camera_list(db: Session):
    return db.query(Camera).all()

# Function for fetching counter list
def get_counter_list(db: Session):
    return db.query(Counter).all()

# Function for fetching ROI list
def get_roi_list(db: Session):
    return db.query(ROI).all()

# Function for fetching visitor list
def get_visitor_list(db: Session):
    return db.query(Visitor).all()
