import os
import cv2
import secrets
import logging
import pandas as pd
from fastapi import Depends, HTTPException, status
from starlette.responses import StreamingResponse
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from db_initialize import Account, Camera, Counter, ROI, Visitor, Activity, Notification
from db_configure import SessionLocal
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy import func, desc, delete
from sqlalchemy.exc import IntegrityError
from typing import Optional, Generator
import psutil  # For CPU, memory, and disk usage
import platform  # For hardware specs
import GPUtil  # For GPU usage and specs (needs 'gputil' library)
from io import BytesIO


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
    username: Optional[str] = None  # Using Optional for compatibility with older Python versions

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
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
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



###########################################################################################
################################ Dashboard Services #######################################
###########################################################################################

# Function to fetch first_name and last_name of the logged-in user
def get_logged_in_user(username: str, db: Session):
    account = db.query(Account).filter(Account.user_name == username).first()
    if account:
        return {"first_name": account.first_name, "last_name": account.last_name}
    else:
        logging.warning(f"User with username {username} not found.")
        return None


# Function to find the least visited counter today and calculate the average duration
def least_visited_counter(db: Session):
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    least_visited_result = (
        db.query(
            Visitor.counter_id,
            func.count(Visitor.person_id).label('visitor_count'),
            func.sum(Visitor.person_duration_in_roi).label('total_duration')
        )
        # the filter to restrict the query to today's visits
        # .filter(Visitor.current_datetime >= today_start)
        .group_by(Visitor.counter_id)
        .order_by(func.count(Visitor.person_id).asc())  # Least visited first
        .first()
    )
    
    if least_visited_result:
        counter_id, visitor_count, total_duration = least_visited_result
        average_duration = round(total_duration / visitor_count, 2) if visitor_count > 0 else 0.00
        return {
            "counter_id": counter_id,
            "visitor_count": visitor_count,
            "average_duration": average_duration
        }
    
    return {"message": "No visitors found today."}

# Function to get total number of visitors
def get_total_visitors(db: Session):
    # Count the total number of visitors
    total_visitors = db.query(func.count(Visitor.person_id)).filter(Visitor.person_id.isnot(None)).scalar()
    
    # Sum the total duration of all visitors in the ROI
    total_duration = db.query(func.sum(Visitor.person_duration_in_roi)).scalar()
    
    # Calculate the average duration per visitor, rounded to two decimal places
    average_duration = round(total_duration / total_visitors, 2) if total_visitors > 0 else 0.00
    
    return {
        "total_visitors": total_visitors,
        "average_duration": average_duration
    }

def most_visited_counter(db: Session):
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    most_visited_result = (
        db.query(
            Visitor.counter_id,
            func.count(Visitor.person_id).label('visitor_count'),
            func.sum(Visitor.person_duration_in_roi).label('total_duration')
        )
        #  The filter to restrict the query to today's visits
        # .filter(Visitor.current_datetime >= today_start)
        .group_by(Visitor.counter_id)
        .order_by(func.count(Visitor.person_id).desc())  # Most visited first
        .first()
    )
    
    if most_visited_result:
        counter_id, visitor_count, total_duration = most_visited_result
        average_duration = round(total_duration / visitor_count, 2) if visitor_count > 0 else 0.00
        return {
            "counter_id": counter_id,
            "visitor_count": visitor_count,
            "average_duration": average_duration
        }
    
    return {"message": "No visitors found today."}

# Function to find the number of age groups of visitors for each counter within the specified date-time
def age_monitoring(selected_date_range: dict, db: Session):
    # Parse the 'start_date' from the request
    start_date = datetime.strptime(selected_date_range['start_date'], '%Y-%m-%d %H:%M:%S')
    # Set the time to 8 AM
    start_date = start_date.replace(hour=8, minute=0, second=0)

    # Parse the 'end_date' from the request
    end_date = datetime.strptime(selected_date_range['end_date'], '%Y-%m-%d %H:%M:%S')

    # Age groups as strings
    age_groups = ['teenager', 'young', 'adult', 'senior']

    # Get distinct counter_ids from the Visitor table
    counters = db.query(Visitor.counter_id).distinct().all()

    # Initialize result list
    result = []

    # Loop through each distinct counter_id
    for counter_tuple in counters:
        counter = counter_tuple[0]  # Extract the counter_id from the tuple
        counter_data = {'counter_id': counter, 'age_groups': {group: 0 for group in age_groups}}
        
        # Loop through each age group and perform the count query
        for group in age_groups:
            count = db.query(func.count(Visitor.id)).filter(
                Visitor.counter_id == counter,
                Visitor.person_age_group == group,  # Compare to the string directly
                Visitor.current_datetime.between(start_date, end_date)  # Filter by datetime range
            ).scalar()  # Use scalar() to get the count result
        
            # Add the count to the counter data under the corresponding age group
            counter_data['age_groups'][group] = count

        # Append the counter data for each counter to the result list
        result.append(counter_data)

    # Return the aggregated result
    return result

# Function to find the number of male and femal visitors for each counter within the specified date-time
def gender_monitoring(selected_date_range: dict, db: Session):
    # Parse the 'start_date' from the request and set the time to 8 AM
    start_date = datetime.strptime(selected_date_range['start_date'], '%Y-%m-%d %H:%M:%S')
    start_date = start_date.replace(hour=8, minute=0, second=0)

    # Parse the 'end_date' from the request
    end_date = datetime.strptime(selected_date_range['end_date'], '%Y-%m-%d %H:%M:%S')

    # Get all distinct counter_ids
    counters = db.query(Visitor.counter_id).distinct().all()

    result = []

    # Loop through each counter and count male/female visitors in the selected date range
    for counter in counters:
        counter_id = counter[0]  # Extract the counter_id

        male_count = db.query(Visitor).filter(
            Visitor.counter_id == counter_id,
            Visitor.person_gender == 'male',
            Visitor.current_datetime.between(start_date, end_date)
        ).count()

        female_count = db.query(Visitor).filter(
            Visitor.counter_id == counter_id,
            Visitor.person_gender == 'female',
            Visitor.current_datetime.between(start_date, end_date)
        ).count()

        # Add the results for the current counter to the response in the desired structure
        result.append({
            "counter_id": counter_id,
            "male": male_count,
            "female": female_count
        })

    return result


def get_system_info():
    """
    Combines both hardware specifications and current usage status
    into a single dictionary.
    """
    # Hardware specifications
    cpu_model = platform.processor()
    memory_info = psutil.virtual_memory()
    memory_total = memory_info.total / (1024 ** 3)  # Convert to GB
    disk_info = psutil.disk_partitions()
    disk_model = disk_info[0].device if disk_info else "N/A"
    gpus = GPUtil.getGPUs()
    gpu_model = gpus[0].name if gpus else "N/A"

    # Current usage status
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = memory_info.percent
    disk_usage = psutil.disk_usage('/').percent
    gpu_usage = gpus[0].load * 100 if gpus else 0  # Use first GPU if available

    return {
        "hardware_specs": {
            "cpu_model": cpu_model,
            "memory_total_gb": memory_total,
            "disk_model": disk_model,
            "gpu_model": gpu_model
        },
        "current_status": {
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "disk_usage": disk_usage,
            "gpu_usage": gpu_usage
        }
    }

# Fetch the latest modified disabled camera
def get_latest_disabled_camera(db: Session):
    # Query to get all disabled cameras, ordered by last modified date descending
    latest_disabled_camera = (
        db.query(Camera)
        .filter(Camera.cam_enable == False)
        .order_by(desc(Camera.cam_last_date_modified))
        .first()  # Get the first result, which will be the latest one
    )

    # Check if a disabled camera was found
    if latest_disabled_camera:
        return {
            "message": f"The camera {latest_disabled_camera.cam_id} is out of reach.",
            "cam_last_date_modified": latest_disabled_camera.cam_last_date_modified
        }
    else:
        return {"message": "No camera is out of reach."}  # Return this message if all cameras are enabled


################################# REPORT PAGE ########################################
################################# REPORT PAGE ########################################
################################# REPORT PAGE ########################################

def get_visitors_by_date_range(db: Session, start_date: str, end_date: str):
    # Convert string dates to datetime objects
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

    # Fetch visitors within the specified date range
    visitors = db.query(Visitor).filter(
        Visitor.current_datetime >= start_datetime,
        Visitor.current_datetime <= end_datetime
    ).all()
    
    return visitors

def get_visitor_records(db: Session, start_date: str, end_date: str, counter_id: int = None, cam_id: int = None, age: str = None, gender: str = None):
    try:
        # Convert string dates to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use 'YYYY-MM-DD'.")

    # Base query
    query = db.query(Visitor).filter(Visitor.current_datetime.between(start_date, end_date))

    # Apply filters if provided
    if counter_id is not None:
        query = query.filter(Visitor.counter_id == counter_id)
    
    if cam_id is not None:
        query = query.filter(Visitor.cam_id == cam_id)

    if age is not None:
        query = query.filter(Visitor.person_age_group == age)

    if gender is not None:
        query = query.filter(Visitor.person_gender == gender)

    # Fetch records
    records = query.all()
    
    if not records:
        raise HTTPException(status_code=404, detail="No records found for the specified criteria.")

    # Prepare data for CSV/Excel export
    data = []
    for idx, record in enumerate(records, start=1):
        data.append({
            "No": idx,
            "Counter ID": record.counter_id,
            "Camera ID": record.cam_id,
            "Person ID": record.person_id,
            "Attendance Duration": record.person_duration_in_roi,
            "Gender": record.person_gender,
            "Age": record.person_age_group,
            "ROI": record.roi_id,
            "Date-Time": record.current_datetime
        })

    return data
def export_visitor_records_to_csv(data):
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer

def export_visitor_records_to_excel(data):
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_excel(buffer, index=False, sheet_name='Visitor Records')
    buffer.seek(0)
    return buffer

# Function to fetch people count per counter from the Visitor table
def get_people_count_per_counter(
    db: Session,
    start_date: str = None,
    end_date: str = None,
    start_time: str = None,
    end_time: str = None
):
    try:
        # Date and time parsing, if provided
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

        if start_time:
            start_time = datetime.strptime(start_time, '%H:%M:%S').time()
        if end_time:
            end_time = datetime.strptime(end_time, '%H:%M:%S').time()

        # Build the query to fetch records where person_id is not None
        query = db.query(Visitor).filter(Visitor.person_id.isnot(None))

        # Apply date and time filters if provided
        if start_date and end_date:
            query = query.filter(Visitor.current_datetime.between(start_date, end_date))

        if start_time and end_time:
            query = query.filter(
                Visitor.current_datetime.between(
                    datetime.combine(start_date, start_time) if start_date else None,
                    datetime.combine(end_date, end_time) if end_date else None
                )
            )

        # Group by counter_id and count total persons
        records = query.with_entities(
            Visitor.counter_id,
            func.count(Visitor.person_id).label("total_persons")
        ).group_by(Visitor.counter_id).all()

        # Check if no records are found
        if not records:
            raise HTTPException(status_code=404, detail="No records found for the specified criteria.")
        
        # Return the result as a list of dicts
        result = [{"counter_id": record.counter_id, "total_persons": record.total_persons} for record in records]
        return result
    
    except ValueError as e:
        # Handle any ValueError due to incorrect date or time format
        raise HTTPException(status_code=400, detail=f"Invalid date or time format: {str(e)}")
    
    except Exception as e:
        # Handle other unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


# Function to fetch people time duration per counter from the Visitor table
def get_people_duration_per_counter(
    db: Session,
    start_date: str = None,
    end_date: str = None,
    start_time: str = None,
    end_time: str = None
):
    try:
        # Date and time parsing, if provided
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

        if start_time:
            start_time = datetime.strptime(start_time, '%H:%M:%S').time()
        if end_time:
            end_time = datetime.strptime(end_time, '%H:%M:%S').time()

        # Build the query to fetch records where person_duration_in_roi is not None
        query = db.query(Visitor).filter(Visitor.person_duration_in_roi.isnot(None))

        # Apply date and time filters if provided
        if start_date and end_date:
            query = query.filter(Visitor.current_datetime.between(start_date, end_date))

        if start_time and end_time:
            query = query.filter(
                Visitor.current_datetime.between(
                    datetime.combine(start_date, start_time) if start_date else None,
                    datetime.combine(end_date, end_time) if end_date else None
                )
            )

        # Group by counter_id and sum total attendance duration
        records = query.with_entities(
            Visitor.counter_id,
            func.sum(Visitor.person_duration_in_roi).label("total_duration")
        ).group_by(Visitor.counter_id).all()

        # Check if no records are found
        if not records:
            raise HTTPException(status_code=404, detail="No records found for the specified criteria.")
        
        # Return the result as a list of dicts
        result = [{"counter_id": record.counter_id, "total_duration": record.total_duration} for record in records]
        return result
    
    except ValueError as e:
        # Handle any ValueError due to incorrect date or time format
        raise HTTPException(status_code=400, detail=f"Invalid date or time format: {str(e)}")
    
    except Exception as e:
        # Handle other unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


# Helper function to serialize SQLAlchemy query results
def serialize_result(result):
    if result is None:
        return None
    if hasattr(result, "_asdict"):  # For tuples from SQLAlchemy queries
        return result._asdict()
    elif isinstance(result, tuple):  # Handle cases where result is a tuple
        return tuple(serialize_result(i) for i in result)
    return result

# This function retrieves various metrics based on the selected counter_id
def report_details_of_selected_counter(db: Session, counter_id: int):
    try:
        # Validate counter_id
        if counter_id <= 0:
            raise HTTPException(status_code=400, detail="Invalid counter_id. It must be a positive integer.")

        # Count total visits for the selected counter
        total_visits = db.query(Visitor).filter(Visitor.counter_id == counter_id, Visitor.person_id.isnot(None)).count()

        # Fetch the most visited date and time
        most_visited_record = db.query(
            Visitor.current_datetime,
            func.count(Visitor.person_id).label("visit_count")
        ).filter(Visitor.counter_id == counter_id, Visitor.person_id.isnot(None)) \
         .group_by(Visitor.current_datetime) \
         .order_by(func.count(Visitor.person_id).desc()).first()

        # Handle case where no visits are found
        if not most_visited_record:
            most_visited_record = (None, 0)

        # Fetch the least visited date and time
        least_visited_record = db.query(
            Visitor.current_datetime,
            func.count(Visitor.person_id).label("visit_count")
        ).filter(Visitor.counter_id == counter_id, Visitor.person_id.isnot(None)) \
         .group_by(Visitor.current_datetime) \
         .order_by(func.count(Visitor.person_id).asc()).first()

        # Handle case where no visits are found
        if not least_visited_record:
            least_visited_record = (None, 0)

        # Calculate total duration of visits in minutes
        total_duration_seconds = db.query(func.sum(Visitor.person_duration_in_roi)).filter(
            Visitor.counter_id == counter_id, Visitor.person_duration_in_roi.isnot(None)
        ).scalar() or 0
        total_duration_minutes = total_duration_seconds / 60

        # Determine the most visited gender
        most_visited_gender = db.query(
            Visitor.person_gender,
            func.count(Visitor.person_gender).label("gender_count")
        ).filter(Visitor.counter_id == counter_id, Visitor.person_gender.isnot(None)) \
         .group_by(Visitor.person_gender) \
         .order_by(func.count(Visitor.person_gender).desc()).first()

        # Handle case where no gender data is found
        if not most_visited_gender:
            most_visited_gender = (None, 0)

        # Determine the most visited age group
        most_visited_age_group = db.query(
            Visitor.person_age_group,
            func.count(Visitor.person_age_group).label("age_count")
        ).filter(Visitor.counter_id == counter_id, Visitor.person_age_group.isnot(None)) \
         .group_by(Visitor.person_age_group) \
         .order_by(func.count(Visitor.person_age_group).desc()).first()

        # Handle case where no age group data is found
        if not most_visited_age_group:
            most_visited_age_group = (None, 0)

        return {
            "total_visits": total_visits,
            "most_visited_datetime": serialize_result(most_visited_record),
            "least_visited_datetime": serialize_result(least_visited_record),
            "total_duration_minutes": total_duration_minutes,
            "most_visited_gender": serialize_result(most_visited_gender),
            "most_visited_age_group": serialize_result(most_visited_age_group),
        }

    except HTTPException as http_exc:
        # Handle HTTPExceptions separately to provide more specific messages
        raise http_exc
    except Exception as e:
        # Log or handle unexpected errors
        raise HTTPException(status_code=500, detail=f"An error occurred while retrieving data: {str(e)}")



################################# CAMERA  ########################################
################################# CAMERA  ########################################
################################# CAMERA  ########################################


VIDEOS_DIRECTORY = "Videos"

def get_most_recent_video(cam_id: int) -> str:
    folder_path = os.path.join(VIDEOS_DIRECTORY, str(cam_id))
    
    if not os.path.exists(folder_path):
        raise HTTPException(status_code=404, detail=f"Folder for camera {cam_id} not found.")
    
    # Retrieve all video files in the folder
    video_files = [f for f in os.listdir(folder_path) if f.endswith(('.mp4', '.avi'))]
    
    if not video_files:
        raise HTTPException(status_code=404, detail=f"No video files found for camera {cam_id}.")
    
    # Parse file names to sort by timestamp
    def extract_timestamp(file_name: str) -> datetime:
        # Format: <cam_id>_YYYY-MM-DD_HH-MM-SS.mp4
        try:
            timestamp_str = file_name.split('_')[1] + "_" + file_name.split('_')[2].split('.')[0]
            return datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid video file format for {file_name}.")
    
    # Sort by date/time descending to get the most recent video
    video_files.sort(key=extract_timestamp, reverse=True)
    most_recent_video = video_files[0]
    most_recent_video_path = os.path.join(folder_path, most_recent_video)
    
    return most_recent_video_path

# Stream video frames
def stream_video_frames(video_path: str) -> Generator:
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise HTTPException(status_code=500, detail="Unable to open video file.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Encode frame as a JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    cap.release()


def get_next_cam_id(db: Session):
    # Get the highest existing cam_id and increment it
    last_camera = db.query(Camera).order_by(Camera.cam_id.desc()).first()
    return (last_camera.cam_id + 1) if last_camera else 1


def insert_camera(db: Session, cam_name: str, cam_ip: str, cam_mac: str, cam_enable: bool, cam_rtsp: str, cam_desc: Optional[str]):
    try:
        # Get the next cam_id
        next_cam_id = get_next_cam_id(db)

        # Create a new Camera instance
        new_camera = Camera(
            cam_id=next_cam_id,
            cam_name=cam_name,
            cam_ip=cam_ip,
            cam_mac=cam_mac,
            cam_enable=cam_enable,  # Use the boolean value from the toggle button
            cam_rtsp=cam_rtsp,
            cam_desc=cam_desc,
            cam_last_date_modified=datetime.now()  # Automatically set the current time
        )

        # Add and commit the new camera
        db.add(new_camera)
        db.commit()
        print(f"New camera inserted with cam_id={next_cam_id}")
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
        raise
    finally:
        db.close()


def delete_camera_by_id(db: Session, cam_id: int):
    try:
        # Check if the camera exists
        camera = db.query(Camera).filter(Camera.cam_id == cam_id).first()
        
        if not camera:
            raise HTTPException(status_code=404, detail=f"Camera with cam_id={cam_id} not found.")

        # If it exists, proceed to delete
        db.execute(delete(Camera).where(Camera.cam_id == cam_id))
        db.commit()
        print(f"Camera with cam_id={cam_id} deleted successfully.")
    
    except Exception as e:
        db.rollback()  # Rollback in case of any error
        print(f"An error occurred: {e}")
        raise
    finally:
        db.close()
    

def camera_details_for_edit(db: Session, cam_id: int):
    try:
        # Fetch the camera details based on cam_id
        camera = db.query(Camera).filter(Camera.cam_id == cam_id).first()
        
        if camera:
            return {
                "cam_ip": camera.cam_ip,
                "cam_mac": camera.cam_mac,
                "cam_enable": camera.cam_enable,
                "cam_rtsp": camera.cam_rtsp,
                "age_detect_status": camera.age_detect_status,
                "gender_detect_status": camera.gender_detect_status,
                "person_counting_status": camera.person_counting_status,
                "time_duration_calculation_status": camera.time_duration_calculation_status
            }
        else:
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def camera_edit_save(
    db: Session, 
    cam_id: int,  # Add cam_id parameter
    cam_name: str, 
    cam_ip: str, 
    cam_mac: str, 
    cam_enable: bool, 
    cam_rtsp: str,
    age_detect_status: bool, 
    gender_detect_status: bool, 
    person_counting_status: bool, 
    time_duration_calculation_status: bool, 
    cam_desc: Optional[str]
):
    try:
        # Fetch the existing camera record to update by cam_id
        camera = db.query(Camera).filter(Camera.cam_id == cam_id).first()

        if not camera:
            raise ValueError(f"Camera with cam_id={cam_id} not found.")

        # Update the camera details
        camera.cam_name = cam_name
        camera.cam_ip = cam_ip
        camera.cam_mac = cam_mac
        camera.cam_enable = cam_enable
        camera.cam_rtsp = cam_rtsp
        camera.age_detect_status = age_detect_status
        camera.gender_detect_status = gender_detect_status
        camera.person_counting_status = person_counting_status
        camera.time_duration_calculation_status = time_duration_calculation_status
        camera.cam_desc = cam_desc  # Update optional description

        # Commit the changes to the database
        db.commit()
        print(f"Camera with cam_id={camera.cam_id} updated successfully.")

    except ValueError as ve:
        print(f"Validation Error: {ve}")
        raise
    except Exception as e:
        db.rollback()
        print(f"An error occurred while updating the camera: {e}")
        raise  # Re-raise the exception for further handling
    finally:
        db.close()








################################# ACCOUNT  ########################################
################################# ACCOUNT  ########################################
################################# ACCOUNT  ########################################

def insert_account(
    db: Session, 
    user_id: int,  # Add user_id parameter
    user_name: str, 
    password: str, 
    email: str, 
    first_name: str, 
    last_name: str, 
    tel: str, 
    user_department: str, 
    user_status: bool
):
    # Check if email or username already exists
    existing_account = db.query(Account).filter((Account.user_id == user_id) | (Account.user_name == user_name)).first()
    
    if existing_account:
        raise HTTPException(status_code=400, detail="This User ID or Username already exists.")
    
    try:
        new_account = Account(
            user_id=user_id,  # Include user_id when creating the account
            user_name=user_name,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            tel=tel,
            user_department=user_department,
            user_status=user_status
        )
        
        db.add(new_account)
        db.commit()
        print(f"New account inserted with user_name={user_name}")
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error inserting account, possibly duplicate username or email.")
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


def delete_user_by_id(db: Session, user_id: int):
    try:
        # Fetch user by user_id
        user = db.query(Account).filter(Account.user_id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail=f"User with user_id={user_id} not found.")

        db.delete(user)  # Delete the user
        db.commit()  # Commit the changes
        print(f"User with user_id={user_id} deleted successfully.")
    
    except Exception as e:
        db.rollback()  # Rollback in case of any error
        print(f"An error occurred while deleting user: {e}")
        raise


def user_details_for_edit(db: Session, user_id: int):
    try:
        user = db.query(Account).filter(Account.user_id == user_id).first()  # Fetch user by user_id
        if not user:
            raise HTTPException(status_code=404, detail=f"User with user_id={user_id} not found.")

        # Return the user details
        return {
            "user_id": user.user_id,
            "user_name": user.user_name,
            "password": user.password,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "tel": user.tel,
            "user_department": user.user_department,
            "user_status": user.user_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching user details: {str(e)}")


def user_edit_save(
    db: Session, 
    user_id: int,  # Use user_id to fetch the record
    user_name: str, 
    password: str, 
    email: str, 
    first_name: str, 
    last_name: str, 
    tel: str, 
    user_department: str, 
    user_status: bool
):
    try:
        # Fetch the user record by user_id
        user = db.query(Account).filter(Account.user_id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail=f"User not found with user_id={user_id}.")

        # Update user details
        user.user_name = user_name
        user.password = password
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.tel = tel
        user.user_department = user_department
        user.user_status = user_status

        db.commit()  # Save the changes to the database
        return {"message": f"User with user_id={user_id} updated successfully."}
    except Exception as e:
        db.rollback()  # Rollback in case of any error
        raise HTTPException(status_code=500, detail=f"An error occurred while updating user: {str(e)}")
