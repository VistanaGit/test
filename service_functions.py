import os
import secrets
import logging
from fastapi import Depends, HTTPException, status
from starlette.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from db_initialize import Account, Camera, Counter, ROI, Visitor, Activity, Notification
from db_configure import SessionLocal
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy import func
import mimetypes  # Ensure this import is included



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

# Function for streaming video
# Function for streaming video
def stream_video(filename: str, frame_rate: int = 10, video_directory: str = "Videos"):
    file_path = os.path.join(video_directory, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video file not found")

    # Determine the correct MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = 'application/octet-stream'  # Fallback type

    # You can implement the frame rate control here (e.g., by skipping frames based on the frame_rate value)

    return StreamingResponse(open(file_path, mode="rb"), media_type=mime_type)



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
