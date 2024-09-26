import os
import secrets
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from db_initialize import Account, Camera, Counter, ROI, Visitor  # Assuming you have these models
from db_configure import SessionLocal
from jose import JWTError, jwt
from datetime import datetime, timedelta

# Get SECRET_KEY from environment or dynamically generation
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))  # Generates a 32-byte hex key if not found in env
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
        raise HTTPException(status_code=404, detail="Email not registered")
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
    credentials_exception = HTTPException(
        status_code=HTTPException.status_code,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return TokenData(username=username)
    except JWTError:
        raise credentials_exception

# Function to handle login
def login(login_data: LoginData, db: Session):
    account = db.query(Account).filter(Account.user_name == login_data.username).first()
    if not account or account.password != login_data.password:
        raise HTTPException(status_code=400, detail="Username or password is wrong")

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
        return {"error": "File not found"}

    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
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
    cameras = db.query(Camera).all()  # Assuming you have a Camera model
    return cameras

# Function to get counter list
def get_counter_list(db: Session):
    counters = db.query(Counter).all()  # Assuming you have a Counter model
    return counters

# Function to get ROI list
def get_roi_list(db: Session):
    rois = db.query(ROI).all()  # Assuming you have an ROI model
    return rois

# Function to get visitor list
def get_visitor_list(db: Session):
    visitors = db.query(Visitor).all()  # Assuming you have a Visitor model
    return visitors
