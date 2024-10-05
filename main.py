import os
import cv2
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import time
import logging


from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db_initialize import Account, Camera, Counter, ROI, Visitor, Activity, Notification
from service_functions import (
    recover_password,
    login,
    get_account_list,  # Ensure this is the correct function
    get_camera_list,
    get_counter_list,
    get_roi_list,
    get_visitor_list,
    get_activity_list,
    get_notification_list,
    get_total_visitors,
    least_visited_counter,
    most_visited_counter,
    age_monitoring,
    gender_monitoring,
    get_system_info,
    PasswordRecoveryData,
    LoginData,
    get_logged_in_user,
    get_latest_disabled_camera,
    get_db,
    verify_token,
    TokenData
)


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

class VideoStreamRequest(BaseModel):
    filename: str

# Endpoint for password recovery
@app.post("/recover_password")
def recover_password_endpoint(recovery_data: PasswordRecoveryData, db: Session = Depends(get_db)):
    return recover_password(recovery_data, db)

# Endpoint to handle login
@app.post("/login")
def login_endpoint(login_data: LoginData, db: Session = Depends(get_db)):
    return login(login_data, db)


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

    # Get the video's frames per second (FPS)
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    frame_duration = 1 / fps  # Time in seconds for each frame

    # Generator function to stream video frames
    def generate_video_stream():
        while video_capture.isOpened():
            start_time = time.time()  # Get the start time of frame processing
            success, frame = video_capture.read()
            if not success:
                break

            # Convert the frame to JPG format
            _, buffer = cv2.imencode('.jpg', frame)

            # Yield the frame as a byte sequence
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n\r\n')

            # Sleep to match the frame duration based on FPS
            elapsed_time = time.time() - start_time
            time.sleep(max(0, frame_duration - elapsed_time))

    # Return streaming response with multipart data
    return StreamingResponse(generate_video_stream(), media_type="multipart/x-mixed-replace; boundary=frame")

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



###########################################################################################
################################ Dashboard Services #######################################
###########################################################################################


# New endpoint to get the logged-in user's details (first_name and last_name)
@app.get("/logged_in_user")
def logged_in_user_endpoint(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Verify token to ensure valid credentials
    token_data = verify_token(token)
    
    if "message" in token_data:
        raise HTTPException(status_code=401, detail=token_data["message"])
    
    try:
        user_details = get_logged_in_user(token_data.username, db)  # Fetch user details
        if user_details:
            return user_details
        else:
            return {"message": "User not found"}
    except Exception as e:
        logging.error(f"Error fetching logged-in user details: {e}")
        raise HTTPException(status_code=500, detail="Error fetching user details")


@app.get("/total_visitors")
async def total_visitors_endpoint(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):    
    token_data = verify_token(token)  # Verifying the token
    try:
        total = get_total_visitors(db)
        return {"total_visitors": total}
    except Exception as e:
        logging.error(f"Error fetching total number of visitors: {e}")
        return {"message": "Error fetching total number of visitors"}
    

# New endpoints for least visited counters
@app.get("/least_visited_counter")
def least_visited_counter_endpoint(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    token_data = verify_token(token)  # Verifying the token
    try:
        result = least_visited_counter(db)
        return result
    except Exception as e:
        logging.error(f"Error fetching least visited counter: {e}")
        return {"message": "Error fetching least visited counter"}

# New endpoints for most visited counters
@app.get("/most_visited_counter")
def most_visited_counter_endpoint(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    token_data = verify_token(token)  # Verifying the token
    try:
        result = most_visited_counter(db)
        return result
    except Exception as e:
        logging.error(f"Error fetching most visited counter: {e}")
        return {"message": "Error fetching most visited counter"}


@app.post("/age_monitoring")
async def age_monitoring_endpoint(selected_date_range: dict, 
                                  db: Session = Depends(get_db),
                                  token: str = Depends(oauth2_scheme)):
    token_data = verify_token(token)  # Verifying the token
    try:
        # Perform age monitoring operation using selected_date_range and db session
        result = age_monitoring(selected_date_range, db)
        return result
    except Exception as e:
        logging.error(f"Error in age monitoring: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/gender_monitoring")
async def gender_monitoring_endpoint(selected_date_range: dict, 
                                    db: Session = Depends(get_db),
                                    token: str = Depends(oauth2_scheme)):
    token_data = verify_token(token)  # Verifying the token    
    try:
        # Perform gender monitoring operation using selected_date_range and db session
        result = gender_monitoring(selected_date_range, db)
        return result
    except Exception as e:
        logging.error(f"Error in gender monitoring: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/system_info")
def get_system_info_route():
    """
    API endpoint to get both hardware specifications and current status.
    """
    system_info = get_system_info()
    return system_info

@app.get("/camera_notification", response_model=dict)
def latest_disabled_camera(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    
    token_data = verify_token(token)  # Verifying the token)
    """
    Fetch the latest modified disabled camera.
    """
    response = get_latest_disabled_camera(db)
    return response  # Return the message from the service function
