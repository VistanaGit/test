from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db_initialize import Account, Camera, Counter, ROI, Visitor 
from service_functions import (
    recover_password,
    login,
    stream_video,
    get_account_list,
    get_camera_list,
    get_counter_list,
    get_roi_list,
    get_visitor_list,
    PasswordRecoveryData,
    LoginData,
    get_db,
    verify_token
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
def stream_video_endpoint(filename: str, frame_rate: int = 10, token: str = Depends(oauth2_scheme)):
    token_data = verify_token(token)  # Verifying the token
    return stream_video(filename, frame_rate, VIDEO_DIRECTORY)

# Database query endpoints (authentication required)

@app.get("/account_list")
def get_account_list(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    token_data = verify_token(token)  # Ensure token is valid
    try:
        accounts = db.query(Account).all()  # Fetch accounts from the database
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
