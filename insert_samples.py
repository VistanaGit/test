from db_configure import SessionLocal
from db_initialize import Account, Camera, Counter, ROI, Visitor, Activity, Notification
from datetime import datetime, timedelta

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
                email='reza@example.com', 
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
        cameras = [
            Camera(cam_name='Camera 1', cam_ip='192.168.1.10', cam_mac='00:0a:95:9d:68:16', cam_enable=True, cam_rtsp='rtsp://camera1', cam_desc='Front Door Camera', cam_last_date_modified='2024-10-01 08:00:00', age_detect_status=False, gender_detect_status=True, person_counting_status=True, time_duration_calculation_status=True, ROI_1='10,20, 30,40', ROI_2=None, ROI_3='90,100, 110,120'),
            Camera(cam_name='Camera 2', cam_ip='192.168.1.11', cam_mac='00:0a:95:9d:68:17', cam_enable=True, cam_rtsp='rtsp://camera2', cam_desc='Back Door Camera', cam_last_date_modified='2024-10-02 10:30:00', age_detect_status=True, gender_detect_status=False, person_counting_status=False, time_duration_calculation_status=True, ROI_1='15,25, 35,45', ROI_2='55,65, 75,85', ROI_3='95,105, 115,125'),
            Camera(cam_name='Camera 3', cam_ip='192.168.1.12', cam_mac='00:0a:95:9d:68:18', cam_enable=False, cam_rtsp='rtsp://camera3', cam_desc='Parking Lot Camera', cam_last_date_modified='2024-10-03 12:15:00', age_detect_status=True, gender_detect_status=True, person_counting_status=True, time_duration_calculation_status=True, ROI_1='20,30, 40,50', ROI_2='60,70, 80,90', ROI_3='100,110, 120,130'),
            Camera(cam_name='Camera 4', cam_ip='192.168.1.13', cam_mac='00:0a:95:9d:68:19', cam_enable=True, cam_rtsp='rtsp://camera4', cam_desc='Lobby Camera', cam_last_date_modified='2024-10-04 14:45:00', age_detect_status=True, gender_detect_status=False, person_counting_status=True, time_duration_calculation_status=False, ROI_1='25,35, 45,55', ROI_2='65,75, 85,95', ROI_3='105,115, 125,135'),
            Camera(cam_name='Camera 5', cam_ip='192.168.1.14', cam_mac='00:0a:95:9d:68:20', cam_enable=False, cam_rtsp='rtsp://camera5', cam_desc='Garage Camera', cam_last_date_modified='2024-10-05 16:00:00', age_detect_status=False, gender_detect_status=True, person_counting_status=False, time_duration_calculation_status=True, ROI_1='30,40, 50,60', ROI_2='70,80, 90,100', ROI_3=None)
        ]
        session.add_all(cameras)
        session.commit()
        print("Cameras inserted successfully!")
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

# Insert ROIs data
def insert_rois():
    session = SessionLocal()
    try:
        rois = [
            ROI(roi_id=1, counter_roi_id=1, roi_coor="[0,0,100,100]", roi_desc="Region 1 for Counter 1"),
            ROI(roi_id=2, counter_roi_id=1, roi_coor="[101,0,200,100]", roi_desc="Region 2 for Counter 1"),
            ROI(roi_id=3, counter_roi_id=2, roi_coor="[0,0,100,100]", roi_desc="Region 1 for Counter 2"),
            ROI(roi_id=4, counter_roi_id=2, roi_coor="[101,0,200,100]", roi_desc="Region 2 for Counter 2"),
            ROI(roi_id=5, counter_roi_id=3, roi_coor="[0,0,100,100]", roi_desc="Region 1 for Counter 3")
        ]
        session.add_all(rois)
        session.commit()
        print("ROIs inserted successfully!")
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
                visitors.append(
                    Visitor(
                        person_id=person_id,
                        roi_id=person_id % 5 + 1,  # Rotate roi_id between 1 and 5
                        counter_id=counter_id,
                        cam_id=counter_id,  # cam_id is the same as counter_id
                        person_duration_in_roi=(person_id * 10) % 300 + 60,  # Random duration pattern
                        person_age_group=['young', 'adult', 'teenager', 'senior'][person_id % 4],
                        person_gender=['male', 'female'][person_id % 2],  # Alternating male/female
                        current_datetime=datetime.now() + timedelta(hours=person_id)
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
