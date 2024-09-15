from sqlalchemy import Column, Integer, String, Text, Boolean, Enum, DateTime
from sqlalchemy.orm import relationship
from db_configure import Base

class Account(Base):
    __tablename__ = 'tbl_accounts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, unique=True, nullable=False)
    user_name = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    tel = Column(String(20))
    user_photo = Column(String(255))
    user_status = Column(Enum('active', 'inactive'))

class Camera(Base):
    __tablename__ = 'tbl_cameras'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cam_id = Column(Integer, unique=True, nullable=False)
    cam_name = Column(String(100))
    cam_ip = Column(String(50))
    cam_mac = Column(String(50))
    cam_enable = Column(Boolean)
    cam_rtsp = Column(String(255))
    cam_desc = Column(Text)

class Counter(Base):
    __tablename__ = 'tbl_counters'

    id = Column(Integer, primary_key=True, autoincrement=True)
    counter_id = Column(Integer, unique=True, nullable=False)
    counter_name = Column(String(100))
    counter_cam_id = Column(Integer)  
    num_of_rois = Column(Integer)
    counter_desc = Column(Text)

class ROI(Base):
    __tablename__ = 'tbl_rois'

    id = Column(Integer, primary_key=True, autoincrement=True)
    roi_id = Column(Integer, unique=True, nullable=False)
    counter_roi_id = Column(Integer)  
    roi_coor = Column(Text)
    roi_desc = Column(Text)

class Visitor(Base):
    __tablename__ = 'tbl_visitors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer)
    roi_id = Column(Integer)  
    counter_id = Column(Integer)  
    cam_id = Column(Integer)  
    person_duration_in_roi = Column(Integer)
    person_age_group = Column(Enum('0', '1', '2'))
    person_gender = Column(Enum('male', 'female'))

class Activity(Base):
    __tablename__ = 'tbl_activities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    activity_name = Column(Enum('login', 'logout'))
    activity_type = Column(Enum('normal', 'abnormal'))
    usr_log_in_date_time = Column(DateTime)
    usr_log_out_date_time = Column(DateTime)
    activity_desc = Column(Text)

class Notification(Base):
    __tablename__ = 'tbl_notifications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    notif_id = Column(Integer, unique=True, nullable=False)
    notif_name = Column(String(100))
    notif_category = Column(String(50))
    notif_desc = Column(Text)
