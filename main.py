import os
import cv2
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import time
import logging
from typing import Optional
from starlette.concurrency import run_in_threadpool  # <-- Import the correct module


from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from db_initialize import Account, Camera, Counter, ROI, Visitor, Activity, Notification
from service_functions import (
    recover_password,
    login,
    get_account_list,
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
    get_visitors_by_date_range,
    export_visitor_records_to_csv,
    export_visitor_records_to_excel,
    get_people_count_per_counter,
    get_people_duration_per_counter,
    report_details_of_selected_counter,
    get_visitor_records,
    get_most_recent_video,
    stream_video_frames,
    insert_camera,
    get_next_cam_id,
    delete_camera_by_id,
    camera_details_for_edit,
    camera_edit_save,
    insert_account,
    delete_user_by_id,
    user_details_for_edit,
    user_edit_save,
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


################################# REPORT PAGE ########################################

@app.post("/report_visitor_table/")
async def report_visitor_table(
    start_date: str,
    end_date: str,
    counter_id: int = None,
    cam_id: int = None,
    age: str = None,
    gender: str = None,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    token_data = verify_token(token)  # Verifying the token
    visitors = get_visitor_records(db, start_date, end_date, counter_id, cam_id, age, gender)
    if not visitors:
        raise HTTPException(status_code=404, detail="No visitors found for the specified date range.")
    
    return {"visitors": visitors}


@app.post("/export_visitor_records/csv")
def export_visitor_records_csv(
    start_date: str,
    end_date: str,
    counter_id: int = None,
    cam_id: int = None,
    age: str = None,
    gender: str = None,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    token_data = verify_token(token)  # Verifying the token
    if not start_date or not end_date:
        raise HTTPException(status_code=400, detail="Start date and end date must be provided.")
    
    data = get_visitor_records(db, start_date, end_date, counter_id, cam_id, age, gender)
    csv_file = export_visitor_records_to_csv(data)
    return StreamingResponse(csv_file, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=visitor_records.csv"})

@app.post("/export_visitor_records/excel")
def export_visitor_records_excel(
    start_date: str,
    end_date: str,
    counter_id: int = None,
    cam_id: int = None,
    age: str = None,
    gender: str = None,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    token_data = verify_token(token)  # Verifying the token
    if not start_date or not end_date:
        raise HTTPException(status_code=400, detail="Start date and end date must be provided.")
    
    data = get_visitor_records(db, start_date, end_date, counter_id, cam_id, age, gender)
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

@app.post("/report_details_of_selected_counter/")
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


################################ CAMERAS ######################################

@app.get("/camera_video_view")
async def camera_video_view(cam_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # Get the most recent video for the selected camera
    try:
        # Verify token
        token_data = verify_token(token)

        video_path = get_most_recent_video(cam_id)
    except HTTPException as e:
        raise e
    
    # Stream the video frames
    return StreamingResponse(stream_video_frames(video_path), media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/insert_camera")
async def insert_camera_service(
    cam_name: str,
    cam_ip: str,
    cam_mac: str,
    cam_enable: bool,  # Boolean value from the toggle switch
    cam_rtsp: str,
    cam_desc: Optional[str] = None,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):

    try:
        # Verify token
        token_data = verify_token(token)

        # Get the next cam_id
        next_cam_id = get_next_cam_id(db)

        # Call the insert_camera function to insert the new record
        insert_camera(db, cam_name, cam_ip, cam_mac, cam_enable, cam_rtsp, cam_desc)

        # Return the next_cam_id as part of the response
        return {"message": f"Camera inserted successfully with cam_id= {next_cam_id}", "cam_id": next_cam_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/delete_camera/{cam_id}")
async def delete_camera_service(cam_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        # Verify token
        token_data = verify_token(token)

        # Call the delete function and pass the session (db)
        delete_camera_by_id(db, cam_id)
        return {"message": f"Camera with cam_id={cam_id} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@app.get("/camera_details_for_edit/{cam_id}")
async def camera_details_for_edit_service(cam_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        # Verify token
        token_data = verify_token(token)
        
        # Call the camera_details_for_edit function from service_functions
        camera_details = camera_details_for_edit(db, cam_id)
        
        if camera_details is not None:
            return {"camera_details": camera_details}
        else:
            raise HTTPException(status_code=404, detail="Camera not found.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@app.put("/camera_edit_save/{cam_id}")
async def camera_edit_save_service(
    cam_id: int,
    cam_ip: str,
    cam_mac: str,
    cam_enable: bool,
    cam_rtsp: str,
    age_detect_status: bool,
    gender_detect_status: bool,
    person_counting_status: bool,
    time_duration_calculation_status: bool,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        # Verify token
        token_data = verify_token(token)
        
        # Call the camera_edit_save function from service_functions
        camera_edit_save(db, cam_id, cam_ip, cam_mac, cam_enable, cam_rtsp, age_detect_status, gender_detect_status, person_counting_status, time_duration_calculation_status)
        return {"message": f"Camera with cam_id= {cam_id} updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


################################ ACCOUNT ######################################

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

@app.post("/insert_account")
async def insert_account_service(
    account_data: AccountCreate,  # Accept JSON body data
    db: Session = Depends(get_db)
):
    try:
        # Verify token
        #token_data = verify_token(token)

        # Call the insert_account function from service_functions
        insert_account(
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
        return {"message": "Account inserted successfully."}
    except HTTPException as e:
        raise e  # re-raise the HTTPException from the service function
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@app.delete("/delete_user/{user_id}")
async def delete_user_service(user_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        # Verify token
        token_data = verify_token(token)
        
        delete_user_by_id(db, user_id)
        return {"message": f"User with user_id={user_id} deleted successfully."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/user_details_for_edit/{user_id}")
async def user_details_for_edit_service(user_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        # Verify token
        token_data = verify_token(token)
        
        user_details = user_details_for_edit(db, user_id)
        return user_details
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the request: {str(e)}")



@app.put("/user_edit_save/{user_id}")
async def user_edit_save_service(user_id: int, user_name: str, password: str, email: str,
                                   first_name: str, last_name: str, tel: str,
                                   user_department: str, user_status: bool, db: Session = Depends(get_db), 
                                   token: str = Depends(oauth2_scheme)):
    try:
        # Verify token
        token_data = verify_token(token)
        
        # Call the user_edit_save function from service_functions
        return user_edit_save(db, user_id, user_name, password, email, first_name, last_name, tel, user_department, user_status)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the request: {str(e)}")
