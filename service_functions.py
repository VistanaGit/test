import os
import secrets
import logging
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from db_initialize import Account, Camera, Counter, ROI, Visitor, Activity, Notification
from db_configure import SessionLocal
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy import func

# Set up logging configuration
logging.basicConfig(level=logging.INFO)

# Get SECRET_KEY from environment or dynamically generate it
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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

# Token data model
class TokenData(BaseModel):
    username: str | None = None

# Password recovery data model for request body
class PasswordRecoveryData(BaseModel):
    email: EmailStr

# Function for password recovery
def recover_password(recovery_data: PasswordRecoveryData, db: Session):
    account = db.query(Account).filter(Account.email == recovery_data.email).first()
    if not account:
        logging.warning("Attempted password recovery with unregistered email: %s", recovery_data.email)
        return {"message": "Email not registered"}
    return {"message": f"Your password is: {account.password}"}

# Function to create a JWT token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to verify and decode JWT token
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logging.warning("Token validation failed: Username not found in token")
            return {"message": "Could not validate credentials"}
        return TokenData(username=username)
    except JWTError as e:
        logging.error("Token validation error: %s", e)
        return {"message": "Could not validate credentials"}

# Function to handle login
def login(login_data: LoginData, db: Session):
    account = db.query(Account).filter(Account.user_name == login_data.username).first()
    
    # If the username or password is incorrect, raise HTTP 401 (Unauthorized) error
    if not account or account.password != login_data.password:
        logging.warning("Login failed for username: %s", login_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Username or password is wrong",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": account.user_name}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"} 

# Function for streaming video (unchanged)
def stream_video(filename: str, frame_rate: int, VIDEO_DIRECTORY: str):
    import cv2
    import os
    import time
    from fastapi.responses import StreamingResponse

    allowed_extensions = [".mp4", ".avi"]
    if not any(filename.endswith(ext) for ext in allowed_extensions):
        return {"error": "Invalid file extension. Only .mp4 and .avi are allowed."}

    video_path = os.path.join(VIDEO_DIRECTORY, filename)
    if not os.path.isfile(video_path):
        logging.error("Video file not found: %s", video_path)
        return {"error": "File not found"}

    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        logging.error("Unable to open video file: %s", video_path)
        return {"error": "Unable to open video file"}

    frame_time = 1.0 / frame_rate  # Time between frames in seconds

    def generate_video_stream():
        while video_capture.isOpened():
            success, frame = video_capture.read()
            if not success:
                break
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n\r\n')
            time.sleep(frame_time)

    return StreamingResponse(generate_video_stream(), media_type="multipart/x-mixed-replace; boundary=frame")

# Function to get account list
def get_account_list(db: Session):
    accounts = db.query(Account).all()
    return accounts

# Function to get camera list
def get_camera_list(db: Session):
    cameras = db.query(Camera).all()  # a Camera model
    return cameras

# Function to get counter list
def get_counter_list(db: Session):
    counters = db.query(Counter).all()  # a Counter model
    return counters

# Function to get ROI list
def get_roi_list(db: Session):
    rois = db.query(ROI).all()  # an ROI model
    return rois

# Function to get visitor list
def get_visitor_list(db: Session):
    visitors = db.query(Visitor).all()  # a Visitor model
    return visitors

# Function to get activity list
def get_activity_list(db: Session):
    activities = db.query(Activity).all()  # an Activity model
    return activities

# Function to get notification list
def get_notification_list(db: Session):
    notifications = db.query(Notification).all()  # a Notification model
    return notifications

# Function to find the least visited counter today
def least_visited_counter(db: Session):
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    least_visited_result = (
        db.query(Visitor.counter_id, func.count(Visitor.persons_count).label('visitor_count'))
          .filter(Visitor.current_datetime >= today_start)
          .group_by(Visitor.counter_id)
          .order_by(func.count(Visitor.persons_count).asc())
          .first()
    )
    
    if least_visited_result:
        counter_id, visitor_count = least_visited_result
        return {"counter_id": counter_id, "visitor_count": visitor_count}
    
    return {"message": "No visitors found today."}

# Function to find the most visited counter today
def most_visited_counter(db: Session):
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    most_visited_result = (
        db.query(Visitor.counter_id, func.count(Visitor.persons_count).label('visitor_count'))
          .filter(Visitor.current_datetime >= today_start)
          .group_by(Visitor.counter_id)
          .order_by(func.count(Visitor.persons_count).desc())
          .first()
    )
    
    if most_visited_result:
        counter_id, visitor_count = most_visited_result
        return {"counter_id": counter_id, "visitor_count": visitor_count}
    
    return {"message": "No visitors found today."}
