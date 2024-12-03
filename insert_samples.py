from db_configure import SessionLocal
from db_initialize import Account, Camera, Counter, ROI, Visitor, Activity, Notification
from datetime import datetime, timedelta
import random

# Insert accounts data
def insert_accounts():
    session = SessionLocal()
    try:
        # Prepare a list of accounts without id, as it's auto-incremented
        accounts = [
            Account(
                user_name='ahmad_hosseini', 
                password='password123', 
                email='ahmad@example.com', 
                first_name='Ahmad', 
                last_name='Hosseini', 
                tel='09123456789', 
                user_department='Department A', 
                user_status=True
            ),
            Account(
                user_name='reza_shokouhi', 
                password='password456', 
                email='vistana.lampada@gmail.com', 
                first_name='Reza', 
                last_name='Shokouhi', 
                tel='09234567890', 
                user_department='Department B', 
                user_status=True
            ),
            Account(
                user_name='fatemeh_ghasemi', 
                password='password789', 
                email='fatemeh@example.com', 
                first_name='Fatemeh', 
                last_name='Ghasemi', 
                tel='09345678901', 
                user_department='Department C', 
                user_status=True
            ),
            Account(
                user_name='mehdi_rahimi', 
                password='password012', 
                email='mehdi@example.com', 
                first_name='Mehdi', 
                last_name='Rahimi', 
                tel='09456789012', 
                user_department='Department D', 
                user_status=False  # Set to False for inactive
            ),
            Account(
                user_name='leila_mohammadi', 
                password='password345', 
                email='leila@example.com', 
                first_name='Leila', 
                last_name='Mohammadi', 
                tel='09567890123', 
                user_department='Department E', 
                user_status=True
            )
        ]
        
        # Add all accounts to the session
        session.add_all(accounts)
        session.commit()
        print("Accounts inserted successfully!")
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        session.close()


# Insert cameras data
def insert_cameras():
    session = SessionLocal()
    try:
        # Sample cameras with various details, including detect status fields
        cameras = [
            Camera(cam_name="Camera 1", cam_ip="192.168.0.101", cam_mac="AA:BB:CC:DD:EE:01", cam_enable=True, cam_rtsp="rtsp://camera1", cam_last_date_modified=datetime.now(), cam_desc="Front door camera", dashboard_display=True, age_detect_status=True, gender_detect_status=True, person_counting_status=True, time_duration_calculation_status=True, exhibition_name="ELECOMP Expo 2024"),
            Camera(cam_name="Camera 2", cam_ip="192.168.0.102", cam_mac="AA:BB:CC:DD:EE:02", cam_enable=True, cam_rtsp="rtsp://camera2", cam_last_date_modified=datetime.now(), cam_desc="Backyard camera", dashboard_display=False, age_detect_status=False, gender_detect_status=True, person_counting_status=True, time_duration_calculation_status=True, exhibition_name="ELECOMP Expo 2024"),
            Camera(cam_name="Camera 3", cam_ip="192.168.0.103", cam_mac="AA:BB:CC:DD:EE:03", cam_enable=True, cam_rtsp="rtsp://camera3", cam_last_date_modified=datetime.now(), cam_desc="Garage camera", dashboard_display=False, age_detect_status=True, gender_detect_status=False, person_counting_status=True, time_duration_calculation_status=True, exhibition_name="ELECOMP Expo 2024"),
            Camera(cam_name="Camera 4", cam_ip="192.168.0.104", cam_mac="AA:BB:CC:DD:EE:04", cam_enable=True, cam_rtsp="rtsp://camera4", cam_last_date_modified=datetime.now(), cam_desc="Living room camera", dashboard_display=False, age_detect_status=True, gender_detect_status=True, person_counting_status=False, time_duration_calculation_status=True, exhibition_name="ELECOMP Expo 2024"),
            Camera(cam_name="Camera 5", cam_ip="192.168.0.105", cam_mac="AA:BB:CC:DD:EE:05", cam_enable=True, cam_rtsp="rtsp://camera5", cam_last_date_modified=datetime.now(), cam_desc="Patio camera", dashboard_display=False, age_detect_status=True, gender_detect_status=True, person_counting_status=True, time_duration_calculation_status=False, exhibition_name="ELECOMP Expo 2024")
        ]
        
        session.add_all(cameras)
        session.commit()
        print("Cameras inserted successfully!")
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        session.close()





def insert_rois():
    session = SessionLocal()
    try:
        # Fetch cameras to link ROIs with the correct camera_id
        cameras = session.query(Camera).all()

        if cameras:
            rois = [
                ROI(roi_name="Region 1 for Camera 1", roi_coor="[10,20,30,40]", roi_desc="Description for Region 1", camera_id=cameras[0].id),
                ROI(roi_name="Region 2 for Camera 1", roi_coor="[50,60,70,80]", roi_desc="Description for Region 2", camera_id=cameras[0].id),
                ROI(roi_name="Region 1 for Camera 2", roi_coor="[15,25,35,45]", roi_desc="Description for Region 1", camera_id=cameras[1].id),
                ROI(roi_name="Region 2 for Camera 2", roi_coor="[55,65,75,85]", roi_desc="Description for Region 2", camera_id=cameras[1].id),
                ROI(roi_name="Region 1 for Camera 3", roi_coor="[20,30,40,50]", roi_desc="Description for Region 1", camera_id=cameras[2].id),
                ROI(roi_name="Region 2 for Camera 3", roi_coor="[60,70,80,90]", roi_desc="Description for Region 2", camera_id=cameras[2].id),
                ROI(roi_name="Region 1 for Camera 4", roi_coor="[25,35,45,55]", roi_desc="Description for Region 1", camera_id=cameras[3].id),
                ROI(roi_name="Region 2 for Camera 4", roi_coor="[65,75,85,95]", roi_desc="Description for Region 2", camera_id=cameras[3].id),
                ROI(roi_name="Region 1 for Camera 5", roi_coor="[30,40,50,60]", roi_desc="Description for Region 1", camera_id=cameras[4].id),
                ROI(roi_name="Region 2 for Camera 5", roi_coor="[70,80,90,100]", roi_desc="Description for Region 2", camera_id=cameras[4].id)
            ]
            session.add_all(rois)
            session.commit()
            print("ROIs inserted successfully!")
        else:
            print("No cameras found to link ROIs.")
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        session.close()




# Insert counters data
def insert_counters():
    session = SessionLocal()
    try:
        counters = [
            Counter(counter_id=1, counter_name='Counter 1', counter_cam_id=1, num_of_rois=2, counter_desc='Main Entrance Counter'),
            Counter(counter_id=2, counter_name='Counter 2', counter_cam_id=2, num_of_rois=3, counter_desc='Back Entrance Counter'),
            Counter(counter_id=3, counter_name='Counter 3', counter_cam_id=3, num_of_rois=1, counter_desc='Parking Lot Counter'),
            Counter(counter_id=4, counter_name='Counter 4', counter_cam_id=4, num_of_rois=4, counter_desc='Lobby Counter'),
            Counter(counter_id=5, counter_name='Counter 5', counter_cam_id=5, num_of_rois=2, counter_desc='Garage Counter')
        ]
        session.add_all(counters)
        session.commit()
        print("Counters inserted successfully!")
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        session.close()


# Insert visitors data
def insert_visitors():
    session = SessionLocal()
    try:
        visitors = []
        person_id_start = 1
        total_records = 50  # Generating 50 records

        # Desired distribution for counter_id
        counter_distribution = {
            1: 6,   # Moderate number of records
            2: 6,   # Moderate number of records
            3: 11,  # Most records for counter_id = 3
            4: 5,   # Less records
            5: 6,   # Moderate number of records
            6: 4,   # Less records
            7: 2,   # Less records
            8: 4,   # Less records
            9: 3,   # Fewer records
            10: 3   # Least records for counter_id = 10
        }

        # Generate visitor records based on distribution
        person_id = person_id_start
        for counter_id, count in counter_distribution.items():
            for _ in range(count):
                # Rotate between today's date, 1 day before, and 2 days before
                base_date = datetime.now().replace(microsecond=0) - timedelta(days=person_id % 3)
                
                # Generate a random time between 7 AM and 11 PM
                random_hour = random.randint(7, 22)  # 7 AM to 10 PM
                random_minute = random.randint(0, 59)
                random_second = random.randint(0, 59)
                
                # Combine base date with random time
                current_datetime = base_date.replace(hour=random_hour, minute=random_minute, second=random_second)

                visitors.append(
                    Visitor(
                        person_id=person_id,
                        roi_id=person_id % 5 + 1,  # Rotate roi_id between 1 and 5
                        counter_id=counter_id,
                        cam_id=counter_id,  # cam_id is the same as counter_id
                        person_duration_in_roi=(person_id * 10) % 300 + 60,  # Random duration pattern
                        person_age_group=['young', 'adult', 'teenager', 'senior'][person_id % 4],
                        person_gender=['male', 'female'][person_id % 2],  # Alternating male/female
                        current_datetime=current_datetime
                    )
                )
                person_id += 1

        session.add_all(visitors)
        session.commit()
        print(f"{len(visitors)} visitors inserted successfully!")
    except Exception as e:
        session.rollback()
        print(f"An error occurred while inserting visitors data: {e}")
    finally:
        session.close()







# Insert activities data
def insert_activities():
    session = SessionLocal()
    try:
        activities = [
            Activity(user_name="ahmad_hosseini", timestamp=datetime.now(), status="Logged In"),
            Activity(user_name="reza_shokouhi", timestamp=datetime.now(), status="Logged Out"),
            Activity(user_name="fatemeh_ghasemi", timestamp=datetime.now(), status="Logged In"),
            Activity(user_name="mehdi_rahimi", timestamp=datetime.now(), status="Logged Out"),
            Activity(user_name="leila_mohammadi", timestamp=datetime.now(), status="Logged In"),
            Activity(user_name="ahmad_hosseini", timestamp=datetime.now(), status="Updated Profile"),
            Activity(user_name="reza_shokouhi", timestamp=datetime.now(), status="Changed Password"),
            Activity(user_name="fatemeh_ghasemi", timestamp=datetime.now(), status="Logged In"),
            Activity(user_name="mehdi_rahimi", timestamp=datetime.now(), status="Logged Out"),
            Activity(user_name="leila_mohammadi", timestamp=datetime.now(), status="Logged In")
        ]
        
        session.add_all(activities)
        session.commit()
        print("Activities inserted successfully!")
    except Exception as e:
        session.rollback()
        print(f"An error occurred while inserting activities data: {e}")
    finally:
        session.close()

# Insert notifications data
def insert_notifications():
    session = SessionLocal()
    try:
        notifications = [
            Notification(notify_text="Welcome to the system!", notify_type=1,
                         timestamp=datetime.now(), desc="User logged in."),
            Notification(notify_text="Your profile has been updated.", notify_type=None,
                         timestamp=datetime.now(), desc="Profile update notification."),
            Notification(notify_text="New visitor detected.", notify_type=None,
                         timestamp=datetime.now(), desc="Visitor detection alert."),
            Notification(notify_text="System maintenance scheduled.", notify_type=None,
                         timestamp=datetime.now(), desc="Maintenance notification."),
            Notification(notify_text="Password changed successfully.", notify_type=None,
                         timestamp=datetime.now(), desc="Password change notification."),
            Notification(notify_text="New camera added.", notify_type=None,
                         timestamp=datetime.now(), desc="Camera addition alert."),
            Notification(notify_text="ROI settings updated.", notify_type=None,
                         timestamp=datetime.now(), desc="ROI update notification."),
            Notification(notify_text="Visitor report generated.", notify_type=None,
                         timestamp=datetime.now(), desc="Report generation alert."),
            Notification(notify_text="User logged out.", notify_type=None,
                         timestamp=datetime.now(), desc="Logout notification."),
            Notification(notify_text="New update available.", notify_type=None,
                         timestamp=datetime.now(), desc="Update notification.")
        ]
        
        # Set default value for notify_type if not provided
        for notification in notifications:
            if notification.notify_type is None:
                notification.notify_type = 1
        
        session.add_all(notifications)
        session.commit()
        print("Notifications inserted successfully!")
    except Exception as e:
        session.rollback()
        print(f"An error occurred while inserting notifications data: {e}")
    finally:
        session.close()

# Main function to run all insert operations
def main():
    insert_accounts()
    insert_cameras()
    insert_counters()
    insert_rois()
    insert_visitors()      # Existing function to insert visitors
    insert_activities()     # New function to insert activities
    insert_notifications()   # New function to insert notifications

if __name__ == "__main__":
    main()
