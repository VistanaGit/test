import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db_initialize import Account, Camera, Counter, ROI, Visitor, Activity, Notification
from service_functions_2 import (
    recover_password,
    login,
    stream_video,
    get_account_list,  # Ensure this is the correct function
    get_camera_list,
    get_counter_list,
    get_roi_list,
    get_visitor_list,
    get_activity_list,
    get_notification_list,
    least_visited_counter,
    most_visited_counter,
    PasswordRecoveryData,
    LoginData,
    get_db,
    verify_token,
    TokenData
)

import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to specific domains as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

VIDEO_DIRECTORY = "Videos/"

# Endpoint for password recovery
@app.post("/recover_password")
def recover_password_endpoint(recovery_data: PasswordRecoveryData, db: Session = Depends(get_db)):
    return recover_password(recovery_data, db)

# Endpoint to handle login
@app.post("/login")
def login_endpoint(login_data: LoginData, db: Session = Depends(get_db)):
    return login(login_data, db)

# Video streaming endpoint (authentication required)
@app.get("/video_play/{filename}")
async def stream_video_endpoint(filename: str, frame_rate: int = 10, token: str = Depends(oauth2_scheme)):
    token_data = verify_token(token)  # Verifying the token
    if not isinstance(token_data, TokenData):  # Ensure the token is valid
        raise HTTPException(status_code=401, detail="Invalid token")
    
    video_path = os.path.join(VIDEO_DIRECTORY, filename)
    if not os.path.isfile(video_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return stream_video(filename, frame_rate, VIDEO_DIRECTORY)


# Database query endpoints (authentication required)
@app.get("/account_list")
def get_account_list_endpoint(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    token_data = verify_token(token)  # Ensure token is valid
    try:
        accounts = db.query(Account).all()  # Fetch accounts from the database using SQLAlchemy ORM
        return accounts
    except Exception as e:
        logging.error(f"Error fetching account list: {e}")  # Log the error for debugging
        return {"message": "Error fetching account list"}  # Return a simple message

@app.get("/camera_list")
def get_camera_list_endpoint(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    token_data = verify_token(token)  # Verifying the token
    try:
        cameras = get_camera_list(db)  # Fetch camera list from the database
        return cameras
    except Exception as e:
        logging.error(f"Error fetching camera list: {e}")  # Log the error for debugging
        return {"message": "Error fetching camera list"}  # Return a simple message

@app.get("/counter_list")
def get_counter_list_endpoint(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    token_data = verify_token(token)  # Verifying the token
    try:
        counters = get_counter_list(db)  # Fetch counter list from the database
        return counters
    except Exception as e:
        logging.error(f"Error fetching counter list: {e}")  # Log the error for debugging
        return {"message": "Error fetching counter list"}  # Return a simple message

@app.get("/roi_list")
def get_roi_list_endpoint(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    token_data = verify_token(token)  # Verifying the token
    try:
        rois = get_roi_list(db)  # Fetch ROI list from the database
        return rois
    except Exception as e:
        logging.error(f"Error fetching ROI list: {e}")  # Log the error for debugging
        return {"message": "Error fetching ROI list"}  # Return a simple message

@app.get("/visitor_list")
def get_visitor_list_endpoint(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    token_data = verify_token(token)  # Verifying the token
    try:
        visitors = get_visitor_list(db)  # Fetch visitor list from the database
        return visitors
    except Exception as e:
        logging.error(f"Error fetching visitor list: {e}")  # Log the error for debugging
        return {"message": "Error fetching visitor list"}  # Return a simple message

@app.get("/activity_list")
def get_activity_list_endpoint(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    token_data = verify_token(token)  # Verifying the token
    try:
        activities = get_activity_list(db)  # Fetch activity list from the database
        return activities
    except Exception as e:
        logging.error(f"Error fetching activity list: {e}")  # Log the error for debugging
        return {"message": "Error fetching activity list"}  # Return a simple message

@app.get("/notification_list")
def get_notification_list_endpoint(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    token_data = verify_token(token)  # Verifying the token
    try:
        notifications = get_notification_list(db)  # Fetch notification list from the database
        return notifications
    except Exception as e:
        logging.error(f"Error fetching notification list: {e}")  # Log the error for debugging
        return {"message": "Error fetching notification list"}  # Return a simple message

# New endpoints for least and most visited counters
@app.get("/least_visited_counter")
def least_visited_counter_endpoint(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    token_data = verify_token(token)  # Verifying the token
    try:
        result = least_visited_counter(db)
        return result
    except Exception as e:
        logging.error(f"Error fetching least visited counter: {e}")
        return {"message": "Error fetching least visited counter"}

@app.get("/most_visited_counter")
def most_visited_counter_endpoint(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    token_data = verify_token(token)  # Verifying the token
    try:
        result = most_visited_counter(db)
        return result
    except Exception as e:
        logging.error(f"Error fetching most visited counter: {e}")
        return {"message": "Error fetching most visited counter"}
