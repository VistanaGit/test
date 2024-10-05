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
from sqlalchemy import func, desc
from typing import Optional
import psutil  # For CPU, memory, and disk usage
import platform  # For hardware specs
import GPUtil  # For GPU usage and specs (needs 'gputil' library)


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


# Function to find the least visited counter today
def least_visited_counter(db: Session):
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    least_visited_result = (
        db.query(Visitor.counter_id, func.count(Visitor.person_id).label('visitor_count'))
          #.filter(Visitor.current_datetime >= today_start)
          .group_by(Visitor.counter_id)
          .order_by(func.count(Visitor.person_id).asc())
          .first()
    )
    
    if least_visited_result:
        counter_id, visitor_count = least_visited_result
        return {"counter_id": counter_id, "visitor_count": visitor_count}
    
    return {"message": "No visitors found today."}

# Function to get total number of visitors
def get_total_visitors(db: Session):
    total_visitors = db.query(func.count(Visitor.person_id)).filter(Visitor.person_id.isnot(None)).scalar()
    return total_visitors

# Function to find the most visited counter today
def most_visited_counter(db: Session):
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    most_visited_result = (
        db.query(Visitor.counter_id, func.count(Visitor.person_id).label('visitor_count'))
          #.filter(Visitor.current_datetime >= today_start)
          .group_by(Visitor.counter_id)
          .order_by(func.count(Visitor.person_id).desc())
          .first()
    )
    
    if most_visited_result:
        counter_id, visitor_count = most_visited_result
        return {"counter_id": counter_id, "visitor_count": visitor_count}
    
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
