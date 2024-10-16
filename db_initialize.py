import logging
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, inspect, ForeignKey
from sqlalchemy.orm import Session, relationship
from db_configure import engine, Base  # Import engine and Base from db_configure
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define UserStatusEnum
class UserStatusEnum(Enum):
    active = 'active'
    inactive = 'inactive'

# Define the Account Model
class Account(Base):
    __tablename__ = 'tbl_accounts'

    id = Column(Integer, primary_key=True, autoincrement=True)  # Ensure id is auto-incrementing
    user_name = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    tel = Column(String)
    user_department = Column(String)
    user_status = Column(Boolean)

# Define the Visitor Model
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

# Define the Camera Model
class Camera(Base):
    __tablename__ = 'tbl_cameras'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cam_name = Column(String)
    cam_ip = Column(String)
    cam_mac = Column(String)
    cam_enable = Column(Boolean)
    cam_rtsp = Column(String)
    age_detect_status = Column(Boolean, default=True)  # Default value can be set to True
    gender_detect_status = Column(Boolean, default=True)
    person_counting_status = Column(Boolean, default=True)
    time_duration_calculation_status = Column(Boolean, default=True)
    cam_last_date_modified = Column(DateTime)
    cam_desc = Column(Text)

    # Relationship with ROI table
    rois = relationship("ROI", back_populates="camera", cascade="all, delete-orphan")


class ROI(Base):
    __tablename__ = 'tbl_rois'

    roi_id = Column(Integer, primary_key=True)
    roi_name = Column(String(50), nullable=True) 
    roi_coor = Column(String, nullable=False)  # Coordinates for the ROI (e.g., JSON string or coordinate format)
    roi_desc = Column(Text)  # Description of the ROI (optional)

    # Foreign key to Camera table
    camera_id = Column(Integer, ForeignKey('tbl_cameras.id'), nullable=False)

    # Relationship with Camera table
    camera = relationship("Camera", back_populates="rois")
    
# Define the Counter Model
class Counter(Base):
    __tablename__ = 'tbl_counters'

    counter_id = Column(Integer, primary_key=True)
    counter_name = Column(String)
    counter_cam_id = Column(Integer)
    num_of_rois = Column(Integer)
    counter_desc = Column(Text)

# Define the Activity Model
class Activity(Base):
    __tablename__ = 'tbl_activity'

    id = Column(Integer, primary_key=True, autoincrement=True)  # Auto-incrementing ID
    user_name = Column(String, nullable=False)  # Username associated with the activity
    timestamp = Column(DateTime, nullable=False)  # Date and time of activity
    status = Column(String)  # Status of activity

# Define the Notifications Model
class Notification(Base):
    __tablename__ = 'tbl_notifications'

    id = Column(Integer, primary_key=True, autoincrement=True)  # Auto-incrementing ID
    notify_text = Column(Text)  # Notification text
    notify_type = Column(Integer, default=1)  # Default value for notify_type is 1
    timestamp = Column(DateTime, nullable=False)  # Date and time of notification
    desc = Column(Text)  # Description of notification

# Function to list all existing tables
def list_tables():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()  # Retrieves the list of table names
    if existing_tables:
        logger.info("Existing tables:")
        for table in existing_tables:
            logger.info(f"- {table}")
    else:
        logger.info("No tables found.")

# Function to drop all tables
def drop_all_tables():
    list_tables()  # List tables before dropping
    logger.info("Starting to drop all tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("All tables have been dropped.")

# Ensure database tables are created
def initialize_db():
    logger.info("Initializing the database...")
    try:
        Base.metadata.create_all(bind=engine)  # This will create the tables
        logger.info("Tables created successfully.")
    except Exception as e:
        logger.error(f"Error during table creation: {e}")

if __name__ == "__main__":
    drop_all_tables()  # Call to drop all tables
    initialize_db()  # Call to initialize the database
