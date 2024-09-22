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
    user_name = Column(String, unique=True)
    password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    tel = Column(String)
    user_photo = Column(String)
    user_status = ENUM(UserStatusEnum, name="user_status_enum")


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
        persons_count = Column(Integer, nullable=False)         
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
    class Counter(Base):
        __tablename__ = 'tbl_counters'

        counter_id = Column(Integer, primary_key=True)
        counter_name = Column(String)
        counter_cam_id = Column(Integer)
        num_of_rois = Column(Integer)
        counter_desc = Column(Text)

    print("Model class for tbl_counters defined successfully.")
except Exception as e:
    print(f"Error defining model class for tbl_counters: {e}")



if __name__ == "__main__":
    from db_configure import engine  # Make sure you have this import

    try:
        Base.metadata.create_all(bind=engine)  # This will create the tbl_accounts table
        print("Table created successfully.")
    except Exception as e:
        print(f"Error during table creation: {e}")
