import os
import cv2
from fastapi import FastAPI, HTTPException, Depends, Query, Path
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import time
import logging
from typing import Optional
from starlette.concurrency import run_in_threadpool  # <-- Import the correct module
import subprocess

from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from db_initialize import Account, Camera, Counter, ROI, Visitor, Activity, Notification
from service_functions_5 import (
    recover_password,
    login,
    get_counter_list,
    get_roi_list,
    get_visitor_list,
    get_activity_list,
    get_notification_list,
    get_total_visitors,
    least_visited_counter,    
    age_monitoring,
    gender_monitoring,
    get_system_info,
    get_visitors_by_date_range,
    export_visitor_records_to_csv,
    export_visitor_records_to_excel,
    get_people_count_per_counter,
    get_people_duration_per_counter,
    report_details_of_selected_counter,
    get_visitor_records,
    get_most_recent_video,
    stream_video_frames,
    get_cameras_details,
    insert_camera,
    delete_camera_by_id,
    camera_details_for_edit,
    camera_edit_save,
    list_rois_for_camera,
    delete_roi_for_camera,
    roi_edit_save,
    get_all_users,
    insert_account,
    delete_user,
    user_details_for_edit,
    user_edit_save,
    add_exhibition,
    list_exhibitions,
    edit_exhibition,
    delete_exhibition,
    get_exhibition_names,
    PasswordRecoveryData,
    LoginData,
    get_logged_in_user,
    get_latest_disabled_camera,
    get_db,
    verify_token,
    TokenData,
    most_visited_counter_no_slot_time_for_latest_date_func,
    most_visited_counter_for_each_slot_time_in_latest_date_func,
    most_visited_counter_for_latest_date_slot_time_func,
    minimum_visited_counter_for_latest_date_slot_time_func,
)

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
def stream_video(filename: str, width: int = 640, height: int = 480):
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

            # Resize the frame to the specified dimensions
            frame = cv2.resize(frame, (width, height))

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



@app.get("/counter_list")
def get_counter_list_endpoint(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    token_data = verify_token(token)  # Verifying the token
    try:
        counters = get_counter_list(db)  # Fetch counter list from the database
        return counters
    except Exception as e:
        logging.error(f"Error fetching counter list: {e}")  # Log the error for debugging
        return {"message": "Error fetching counter list"}  # Return a simple message



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




################################ Dashboard APIs ###################################



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
async def total_visitors_endpoint(db: Session = Depends(get_db)):    
    #token_data = verify_token(token)  # Verifying the token
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

# New endpoints for retrieving of most visited counter with no slot time and only for latest date (today) - on home dashboard
@app.get("/most_visited_counter_no_slot_time_for_latest_date")
def most_visited_counter_no_slot_time_for_latest_date_endpoint(db: Session = Depends(get_db)):
    #token_data = verify_token(token)  # Verifying the token
    try:
        result = most_visited_counter_no_slot_time_for_latest_date_func(db)
        return result
    except Exception as e:
        logging.error(f"Error fetching most visited counter: {e}")
        return {"message": "Error fetching most visited counter"}




# New endpoints for retrieving of most visited counter for only latest date and covering slot time
@app.get("/most_visited_counter_for_each_slot_time_in_latest_date")
def most_visited_counter_for_each_slot_time_in_latest_date_endpoint(db: Session = Depends(get_db)):
    #token_data = verify_token(token)  # Verifying the token
    try:
        result = most_visited_counter_for_each_slot_time_in_latest_date_func(db)
        return result
    except Exception as e:
        logging.error(f"Error fetching most visited counter: {e}")
        return {"message": "Error fetching most visited counter"}



# Endpoint for identifying the most visited counter during specific time slots on the latest date stored in the database.
@app.get("/most_visited_counter_for_latest_date_slot_time")
def most_visited_counter_for_latest_date_slot_time_endpoint(db: Session = Depends(get_db)):
    #token_data = verify_token(token)  # Verifying the token
    try:
        result = most_visited_counter_for_latest_date_slot_time_func(db)
        return result
    except Exception as e:
        logging.error(f"Error fetching most visited counter: {e}")
        return {"message": "Error fetching most visited counter"}


# New endpoint to find the minimum visited counter for the latest date
@app.get("/minimum_visited_counter_for_latest_date_slot_time")
def minimum_visited_counter_for_latest_date_slot_time_endpoint(db: Session = Depends(get_db)):
    try:
        result = minimum_visited_counter_for_latest_date_slot_time_func(db)
        return result
    except Exception as e:
        logging.error(f"Error fetching minimum visited counter: {e}")
        return {"message": "Error fetching minimum visited counter"}
        


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
def get_system_info_route(token: str = Depends(oauth2_scheme)):
    """
    API endpoint to get both hardware specifications and current status.
    """
    token_data = verify_token(token)  # Verifying the token)

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


################################# REPORT APIs ###################################

@app.get("/report_visitor_table/") 
async def report_visitor_table(
    start_date: str,
    end_date: str,
    counter_id: int = None,
    id: int = None,
    age: str = None,
    gender: str = None,
    db: Session = Depends(get_db)
):
    #token_data = verify_token(token)  # Verifying the token
    visitors = get_visitor_records(db, start_date, end_date, counter_id, id, age, gender)
    
    # Instead of raising 404, return the visitors data which could be empty
    return {"visitors": visitors}


@app.post("/export_visitor_records/csv")
def export_visitor_records_csv(
    start_date: str,
    end_date: str,
    counter_id: int = None,
    id: int = None,
    age: str = None,
    gender: str = None,
    exhibition: str = None,
    db: Session = Depends(get_db)
):
    #token_data = verify_token(token)  # Verifying the token
    if not start_date or not end_date:
        raise HTTPException(status_code=400, detail="Start date and end date must be provided.")
    
    data = get_visitor_records(db, start_date, end_date, counter_id, id, age, gender, exhibition)
    csv_file = export_visitor_records_to_csv(data)
    return StreamingResponse(csv_file, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=visitor_records.csv"})

@app.post("/export_visitor_records/excel")
def export_visitor_records_excel(
    start_date: str,
    end_date: str,
    counter_id: int = None,
    id: int = None,
    age: str = None,
    gender: str = None,
    exhibition: str = None,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    token_data = verify_token(token)  # Verifying the token
    if not start_date or not end_date:
        raise HTTPException(status_code=400, detail="Start date and end date must be provided.")
    
    data = get_visitor_records(db, start_date, end_date, counter_id, id, age, gender, exhibition)
    excel_file = export_visitor_records_to_excel(data)
    return StreamingResponse(excel_file, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": "attachment; filename=visitor_records.xlsx"})



# Endpoint for reporting people count per counter
@app.post("/report_people_count_per_counter/")
def report_people_count_per_counter(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    # Verify the token
    token_data = verify_token(token)  # Verifying the token

    try:
        # Fetch data from service_functions
        people_count = get_people_count_per_counter(
            db=db,
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # If no data found, return 404
    if not people_count:
        raise HTTPException(status_code=404, detail="No data found for the given criteria.")

    return {"result": people_count}


@app.post("/report_people_duration_per_counter/")
async def report_people_duration_per_counter(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        # Verify token
        token_data = verify_token(token)
        
        # Fetch the total attendance duration per counter
        result = get_people_duration_per_counter(db, start_date, end_date, start_time, end_time)
        
        if not result:
            raise HTTPException(status_code=404, detail="No records found for the specified criteria.")
        
        return {"total_duration_per_counter": result}
    
    except HTTPException as e:
        # Handle known HTTPExceptions and pass them through
        raise e
    
    except ValueError as e:
        # Handle value-related issues (e.g., date or time parsing errors)
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/report_details_of_selected_counter/{counter_id}")
async def report_details_of_selected_counter_route(
    counter_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        # Verify token
        token_data = verify_token(token)

        # Run the synchronous function in a threadpool to avoid blocking
        result = await run_in_threadpool(report_details_of_selected_counter, db, counter_id)

        return {"details": result}

    except HTTPException as e:
        # Handle known HTTPExceptions and pass them through
        raise e

    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")



################################ CAMERAS APIs ######################################

@app.get("/cameras")
def get_camera_list_endpoint(db: Session = Depends(get_db)
):
    # Verifying the token
    #token_data = verify_token(token)  

    try:
        cameras = get_cameras_details(db)  # Fetch camera list from the database
        return cameras
    except Exception as e:
        logging.error(f"Error fetching camera list: {e}")  # Log the error for debugging
        raise HTTPException(status_code=500, detail="Error fetching camera list")  # Raise an HTTP exception for error handling

# Define the Pydantic model for Camera data
class CameraData(BaseModel):
    cam_name: str
    cam_ip: str
    cam_mac: str
    cam_enable: bool
    cam_rtsp: str
    exhibition_id: int
    cam_desc: Optional[str] = None

@app.post("/cameras")
async def insert_camera_service(
    camera_data: CameraData,  # Use Pydantic model to receive the data
    db: Session = Depends(get_db)
):
    try:
        # Verify token
        #token_data = verify_token(token)

        # Call the insert_camera function to insert the new record
        insert_camera(
            db=db,
            cam_name=camera_data.cam_name,
            cam_ip=camera_data.cam_ip,
            cam_mac=camera_data.cam_mac,
            cam_enable=camera_data.cam_enable,
            cam_rtsp=camera_data.cam_rtsp,            
            exhibition_id=camera_data.exhibition_id,
            cam_desc=camera_data.cam_desc
        )

        # Return a success message
        return {"message": "Camera inserted successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/cameras/{id}")
async def delete_camera_service(
    id: int,  # Accept the camera ID as a path parameter
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        # Verify token
        token_data = verify_token(token)

        # Call the delete function and pass the session (db)
        delete_camera_by_id(db, id)  # Pass id from the path parameter
        return {"message": f"Camera with id={id} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/cameras/{id}")
async def camera_details_for_edit_service(
    id: int,  # Accept the camera ID as a path parameter
    db: Session = Depends(get_db)
):
    try:
        # Verify token
        #token_data = verify_token(token)

        # Call the camera_details_for_edit function from service_functions
        camera_details = camera_details_for_edit(db, id)  # Use id from path parameter
        
        if camera_details is not None:
            return {"camera_details": camera_details}
        else:
            raise HTTPException(status_code=404, detail="Camera not found.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Pydantic model for camera edit data
class CameraEditData(BaseModel):
    cam_name: str
    cam_ip: str
    cam_mac: str
    cam_enable: bool
    cam_rtsp: str
    exhibition_id: int
    age_detect_status: bool
    gender_detect_status: bool
    person_counting_status: bool
    time_duration_calculation_status: bool
    cam_desc: Optional[str] = None  # Optional description

@app.patch("/cameras/{id}")  # Optionally allow PATCH as well
async def camera_edit_save_service(
    id: int,  # Accept id as a path parameter
    camera_data: CameraEditData,
    db: Session = Depends(get_db)
):
    try:
        # Verify token
        #token_data = verify_token(token)

        # Call the camera_edit_save function from service_functions
        camera_edit_save(
            db=db,
            id=id,  # Pass id from the path parameter
            cam_name=camera_data.cam_name,
            cam_ip=camera_data.cam_ip,
            cam_mac=camera_data.cam_mac,
            cam_enable=camera_data.cam_enable,
            cam_rtsp=camera_data.cam_rtsp,
            exhibition_id=camera_data.exhibition_id,
            age_detect_status=camera_data.age_detect_status,
            gender_detect_status=camera_data.gender_detect_status,
            person_counting_status=camera_data.person_counting_status,
            time_duration_calculation_status=camera_data.time_duration_calculation_status,
            cam_desc=camera_data.cam_desc  # Pass optional description
        )
        return {"message": f"Camera with ID {id} updated successfully."}  # Include camera ID in the response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/camera_video_view")
async def camera_video_view(id: int, db: Session = Depends(get_db)):
    # Get the most recent video for the selected camera
    try:
        # Verify token
        #token_data = verify_token(token)

        video_path = get_most_recent_video(id)
    except HTTPException as e:
        raise e
    
    # Stream the video frames
    return StreamingResponse(stream_video_frames(video_path), media_type="multipart/x-mixed-replace; boundary=frame")





#################################### ROIS APIs ######################################

# ROI Update Schema
class ROIData(BaseModel):
    roi_name: str
    roi_coor: str  # Coordinates for the ROI
    roi_desc: Optional[str] = None  # Optional description


## List of ROIs service
@app.get("/rois/{camera_id}")
def list_rois(camera_id: int, db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)):
    try:
        # Verify token
        token_data = verify_token(token)
        
        # Fetch all ROIs for the selected camera
        rois = list_rois_for_camera(db, camera_id)
        
        if rois:
            return {"camera_id": camera_id, "rois": rois}
        else:
            raise HTTPException(status_code=404, detail=f"No ROIs found for Camera ID {camera_id}.")
    
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Delete ROI service
@app.delete("/rois/{camera_id}/{roi_id}")
def delete_roi(camera_id: int, roi_id: int, db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)):
    try:
        # Verify token
        token_data = verify_token(token)

        # Delete the selected ROI
        result = delete_roi_for_camera(db, camera_id, roi_id)
        
        if result:
            return {"message": f"ROI with ID {roi_id} for Camera ID {camera_id} deleted successfully."}
        else:
            raise HTTPException(status_code=404, detail="Camera or ROI not found.")
    
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")



# ROI Edit Endpoint
@app.patch("/rois/{camera_id}/{roi_id}")
async def roi_edit_service(
    camera_id: int,  # Accept camera_id as a path parameter
    roi_id: int,  # Accept roi_id as a path parameter
    roi_data: ROIData,  # Accept the ROI details as a request body
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        # Verify token
        token_data = verify_token(token)

        # Call the roi_edit_save function from service_functions
        roi_edit_save(
            db=db,
            camera_id=camera_id,
            roi_id=roi_id,
            roi_name=roi_data.roi_name,
            roi_coor=roi_data.roi_coor,
            roi_desc=roi_data.roi_desc  # Pass optional description
        )
        return {"message": f"ROI with ID {roi_id} for Camera ID {camera_id} updated successfully."}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


## add camera
@app.post("/rois/{camera_id}")
async def insert_roi(camera_id: int):
    try:
        # Run the Python script with the specified camera ID
        result = subprocess.run(['python3', 'roi_define/roi_definition.py', '--video', str(camera_id)], capture_output=True, text=True)
        return {"output": result.stdout}
    except Exception as e:
        return {"error": str(e)}


################################ ACCOUNTS APIs ######################################

# Creat users service to fetch all users
@app.get("/users")
async def get_all_users_service(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        # Verify token
        token_data = verify_token(token)

        # Fetch all user accounts by calling the service function
        users = get_all_users(db)
        
        return users
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching the users: {str(e)}")





# Create a Pydantic model for the account data
class AccountCreate(BaseModel):
    user_name: str
    password: str
    email: str
    first_name: str
    last_name: str
    tel: str
    user_department: str
    user_status: bool

@app.post("/users")
async def insert_account_service(
    account_data: AccountCreate,  # Accept JSON body data
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        # Verify token
        token_data = verify_token(token)

        # Call the insert_account function from service_functions
        new_account = insert_account(
            db=db,
            user_name=account_data.user_name,
            password=account_data.password,
            email=account_data.email,
            first_name=account_data.first_name,
            last_name=account_data.last_name,
            tel=account_data.tel,
            user_department=account_data.user_department,
            user_status=account_data.user_status
        )
        return {"message": "Account inserted successfully.", "id": new_account.id}
    except HTTPException as e:
        raise e  # Re-raise the HTTPException from the service function
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))





class UserDeleteRequest(BaseModel):
    id: int  # The user ID to delete


@app.delete("/users/{id}")
async def delete_user_service(
    id: int = Path(..., description="The ID of the user to delete"),  # id as a path parameter
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        # Verify token
        token_data = verify_token(token)

        # Call the delete_user function from service_functions
        return delete_user(db, id)  # Use id from the path parameter
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the request: {str(e)}")



@app.get("/users/{id}")
async def user_details_for_edit_service(
    id: int = Path(..., description="The ID of the user to retrieve details for"),  # id as a path parameter
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        # Verify token
        token_data = verify_token(token)

        # Call the user_details_for_edit function from service_functions
        user_details = user_details_for_edit(db, id)  # Use id from the path parameter
        
        return user_details  # Return the user details
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the request: {str(e)}")



# Pydantic model for user data (excluding id)
class UserEdit(BaseModel):
    user_name: str
    password: str
    email: str
    first_name: str
    last_name: str
    tel: str
    user_department: str
    user_status: bool

@app.put("/users/{id}")
async def user_edit_save_service(
    user_data: UserEdit,  # Non-default argument (Pydantic model for user data)
    id: int = Path(..., description="The ID of the user to edit"),  # Default argument
    db: Session = Depends(get_db),  # Default argument
    token: str = Depends(oauth2_scheme)  # Default argument
):
    try:
        # Verify token
        token_data = verify_token(token)

        # Call the user_edit_save function from service_functions and pass id
        return user_edit_save(
            db=db,
            id=id,  # Use id from the path
            user_name=user_data.user_name,
            password=user_data.password,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            tel=user_data.tel,
            user_department=user_data.user_department,
            user_status=user_data.user_status
        )
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the request: {str(e)}")




@app.post("/exhibitions/")
async def add_exhibition_service(
    name: str,
    description: str,
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
):
    try:
        new_exhibition = add_exhibition(db, name, description, start_date, end_date)
        return {"message": "Exhibition added successfully", "exhibition": new_exhibition}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# List all exhibitions
@app.get("/exhibitions/")
async def list_exhibitions_service(db: Session = Depends(get_db)):
    exhibitions = list_exhibitions(db)
    if not exhibitions:
        raise HTTPException(status_code=404, detail="No exhibitions found")
    return {"exhibitions": exhibitions}

# Edit an exhibition
@app.put("/exhibitions/{exhibition_id}")
async def edit_exhibition_service(
    exhibition_id: int,
    name: str,
    description: str,
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
):
    updated_exhibition = edit_exhibition(db, exhibition_id, name, description, start_date, end_date)
    if updated_exhibition:
        return {"message": "Exhibition updated successfully", "exhibition": updated_exhibition}
    else:
        raise HTTPException(status_code=404, detail="Exhibition not found")

# Delete an exhibition
@app.delete("/exhibitions/{exhibition_id}")
async def delete_exhibition_service(exhibition_id: int, db: Session = Depends(get_db)):
    success = delete_exhibition(db, exhibition_id)
    if success:
        return {"message": "Exhibition deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Exhibition not found")


# Endpoint to list exhibition names
@app.get("/exhibitions/names")
def get_exhibition_names_endpoint(db: Session = Depends(get_db)):
    # Verifying the token
    #token_data = verify_token(token)  

    try:
        exhibition_names = get_exhibition_names(db)  # Fetch exhibition names from the database
        return exhibition_names
    except Exception as e:
        logging.error(f"Error fetching exhibition names: {e}")  # Log the error for debugging
        raise HTTPException(status_code=500, detail="Error fetching exhibition names")  # Raise an HTTP exception for error handling
