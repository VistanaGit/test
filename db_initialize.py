from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ENUM
from enum import Enum as PyEnum

# Initialize the Base class
Base = declarative_base()

# Define UserStatusEnum
class UserStatusEnum(PyEnum):
    active = 'active'
    inactive = 'inactive'

# Define the Account Model
class Account(Base):
    __tablename__ = 'tbl_accounts'

    user_id = Column(Integer, primary_key=True)
    user_name = Column(String, unique=True, nullable=False)  # Ensure username is not null
    password = Column(String, nullable=False)  # Ensure password is not null
    email = Column(String, unique=True, nullable=False)  # Ensure email is not null
    first_name = Column(String)
    last_name = Column(String)
    tel = Column(String)
    user_photo = Column(String)
    user_status = Column(ENUM(UserStatusEnum, name="user_status_enum"), default='active')  # Add default status

# Define the Visitor Model
try:
    class Visitor(Base):
        __tablename__ = 'tbl_visitors'

        id = Column(Integer, primary_key=True, autoincrement=True)
        person_id = Column(Integer)
        roi_id = Column(Integer)
        counter_id = Column(Integer)
        cam_id = Column(Integer)
        person_duration_in_roi = Column(Float, nullable=False)
        person_age_group = Column(String)
        person_gender = Column(String)    
        current_datetime = Column(DateTime, nullable=False)

    print("Model class for tbl_visitors defined successfully.")
except Exception as e:
    print(f"Error defining model class for tbl_visitors: {e}")

# Define the Camera Model
try:
    class Camera(Base):
        __tablename__ = 'tbl_cameras'

        cam_id = Column(Integer, primary_key=True)
        cam_name = Column(String)
        cam_ip = Column(String)
        cam_mac = Column(String)
        cam_enable = Column(Boolean)
        cam_rtsp = Column(String)
        cam_last_date_modified = Column(DateTime)
        cam_desc = Column(Text)

    print("Model class for tbl_cameras defined successfully.")
except Exception as e:
    print(f"Error defining model class for tbl_cameras: {e}")

# Define the ROI Model
try:
    class ROI(Base):
        __tablename__ = 'tbl_rois'

        roi_id = Column(Integer, primary_key=True)
        counter_roi_id = Column(Integer)
        roi_coor = Column(String)
        roi_desc = Column(Text)

    print("Model class for tbl_rois defined successfully.")
except Exception as e:
    print(f"Error defining model class for tbl_rois: {e}")

# Define the Counter Model
try:
    class Counter(Base):  # Added Base inheritance to ensure it's a model
        __tablename__ = 'tbl_counters'

        counter_id = Column(Integer, primary_key=True)
        counter_name = Column(String)
        counter_cam_id = Column(Integer)
        num_of_rois = Column(Integer)
        counter_desc = Column(Text)

    print("Model class for tbl_counters defined successfully.")
except Exception as e:
    print(f"Error defining model class for tbl_counters: {e}")


# Define the Activity Model
try:
    class Activity(Base):
        __tablename__ = 'tbl_activity'

        id = Column(Integer, primary_key=True, autoincrement=True)  # Auto-incrementing ID
        user_name = Column(String, nullable=False)  # Username associated with the activity
        timestamp = Column(DateTime, nullable=False)  # Date and time of activity
        status = Column(String)  # Status of activity

    print("Model class for tbl_activity defined successfully.")
except Exception as e:
    print(f"Error defining model class for tbl_activity: {e}")

# Define the Notifications Model
try:
    class Notification(Base):
        __tablename__ = 'tbl_notifications'

        id = Column(Integer, primary_key=True, autoincrement=True)  # Auto-incrementing ID
        notify_text = Column(Text)  # Notification text
        notify_type = Column(Integer, default=1)  # Default value for notify_type is 1
        timestamp = Column(DateTime, nullable=False)  # Date and time of notification
        desc = Column(Text)  # Description of notification

    print("Model class for tbl_notifications defined successfully.")
except Exception as e:
    print(f"Error defining model class for tbl_notifications: {e}")


# Ensure database tables are created
if __name__ == "__main__":
    from db_configure import engine  # Make sure you have this import

    try:
        Base.metadata.create_all(bind=engine)  # This will create the tbl_accounts table and other tables
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error during table creation: {e}")
