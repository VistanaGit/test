from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
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
    get_db
)

# Initialize FastAPI application
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to specific domains as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VIDEO_DIRECTORY = "Videos/"

# Endpoint for password recovery
@app.post("/recover_password")
def recover_password_endpoint(recovery_data: PasswordRecoveryData, db: Session = Depends(get_db)):
    return recover_password(recovery_data, db)

# Endpoint to handle login
@app.post("/login")
def login_endpoint(login_data: LoginData, db: Session = Depends(get_db)):
    return login(login_data, db)

# Video streaming endpoint
@app.get("/video_play/{filename}")
def stream_video_endpoint(filename: str, frame_rate: int = 10):
    return stream_video(filename, frame_rate, VIDEO_DIRECTORY)

# Endpoints for database queries
@app.get("/account_list")
def get_account_list_endpoint(db: Session = Depends(get_db)):
    return get_account_list(db)

@app.get("/camera_list")
def get_camera_list_endpoint(db: Session = Depends(get_db)):
    return get_camera_list(db)

@app.get("/counter_list")
def get_counter_list_endpoint(db: Session = Depends(get_db)):
    return get_counter_list(db)

@app.get("/roi_list")
def get_roi_list_endpoint(db: Session = Depends(get_db)):
    return get_roi_list(db)

@app.get("/visitor_list")
def get_visitor_list_endpoint(db: Session = Depends(get_db)):
    return get_visitor_list(db)
