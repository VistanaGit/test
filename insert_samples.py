from db_configure import SessionLocal
from db_initialize import Account, Camera, Counter, ROI, Visitor, Activity, Notification
from datetime import datetime, timedelta

# Insert accounts data
def insert_accounts():
    session = SessionLocal()
    try:
        accounts = [
            Account(user_id=1001, user_name='ahmad_hosseini', password='password123', email='ahmad@example.com', first_name='Ahmad', last_name='Hosseini', tel='09123456789', user_photo='ahmad_hosseini.jpg', user_status='active'),
            Account(user_id=1002, user_name='reza_shokouhi', password='password456', email='reza@example.com', first_name='Reza', last_name='Shokouhi', tel='09234567890', user_photo='reza_shokouhi.jpg', user_status='active'),
            Account(user_id=1003, user_name='fatemeh_ghasemi', password='password789', email='fatemeh@example.com', first_name='Fatemeh', last_name='Ghasemi', tel='09345678901', user_photo='fatemeh_ghasemi.jpg', user_status='active'),
            Account(user_id=1004, user_name='mehdi_rahimi', password='password012', email='mehdi@example.com', first_name='Mehdi', last_name='Rahimi', tel='09456789012', user_photo='mehdi_rahimi.jpg', user_status='inactive'),
            Account(user_id=1005, user_name='leila_mohammadi', password='password345', email='leila@example.com', first_name='Leila', last_name='Mohammadi', tel='09567890123', user_photo='leila_mohammadi.jpg', user_status='active')
        ]
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
            Camera(cam_id=1, cam_name='Camera 1', cam_ip='192.168.1.10', cam_mac='00:0a:95:9d:68:16', cam_enable=True, cam_rtsp='rtsp://camera1', cam_desc='Front Door Camera'),
            Camera(cam_id=2, cam_name='Camera 2', cam_ip='192.168.1.11', cam_mac='00:0a:95:9d:68:17', cam_enable=True, cam_rtsp='rtsp://camera2', cam_desc='Back Door Camera'),
            Camera(cam_id=3, cam_name='Camera 3', cam_ip='192.168.1.12', cam_mac='00:0a:95:9d:68:18', cam_enable=False, cam_rtsp='rtsp://camera3', cam_desc='Parking Lot Camera'),
            Camera(cam_id=4, cam_name='Camera 4', cam_ip='192.168.1.13', cam_mac='00:0a:95:9d:68:19', cam_enable=True, cam_rtsp='rtsp://camera4', cam_desc='Lobby Camera'),
            Camera(cam_id=5, cam_name='Camera 5', cam_ip='192.168.1.14', cam_mac='00:0a:95:9d:68:20', cam_enable=False, cam_rtsp='rtsp://camera5', cam_desc='Garage Camera')
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
        visitors = [
            Visitor(person_id=1, roi_id=1, counter_id=1,
                    cam_id=1,
                    person_duration_in_roi=120,
                    person_age_group="young",
                    person_gender="male",
                    current_datetime=datetime(2024, 9, 19, 10)),
            Visitor(person_id=2,
                    roi_id=2,
                    counter_id=1,
                    cam_id=1,
                    person_duration_in_roi=150,
                    person_age_group="adult",
                    person_gender="female",
                    current_datetime=datetime(2024, 9, 19, 11)),
            Visitor(person_id=3,
                    roi_id=3,
                    counter_id=2,
                    cam_id=2,
                    person_duration_in_roi=90,
                    person_age_group="teenager",
                    person_gender="male",
                    current_datetime=datetime(2024, 9, 27, 12)),
            Visitor(person_id=4,
                    roi_id=4,
                    counter_id=2,
                    cam_id=2,
                    person_duration_in_roi=110,
                    person_age_group="young",
                    person_gender="female",
                    current_datetime=datetime(2024, 9, 19, 13)),
            Visitor(person_id=5,
                    roi_id=5,
                    counter_id=3,
                    cam_id=3,
                    person_duration_in_roi=200,
                    person_age_group="senior",
                    person_gender="male",
                    current_datetime=datetime(2024, 9, 27, 14))
        ]

        # Ensure the desired distribution of counter_ids
        counter_1_count = 5  # Already inserted 2 records for counter_id 1
        counter_2_count = 2  # Already inserted 2 records for counter_id 2
        counter_3_count = 1  # Already inserted 1 record for counter_id 3

        for i in range(6, 31):
            if counter_1_count < 7:
                counter_id = 1
                counter_1_count += 1
            elif counter_2_count < 9:
                counter_id = 2
                counter_2_count += 1
            else:
                counter_id = 3
                counter_3_count += 1

            visitors.append(
                Visitor(
                    person_id=i,
                    roi_id=i % 5 + 1,
                    counter_id=counter_id,
                    cam_id=(i - 1) % 3 + 1,
                    person_duration_in_roi=(i * 10) % 300 + 60,
                    person_age_group=['young', 'adult', 'teenager', 'senior', 'young'][i % 5],
                    person_gender=['male', 'female'][i % 2],
                    current_datetime=datetime.now() + timedelta(hours=i)
                )
            )

        session.add_all(visitors)
        session.commit()
        print("Visitors inserted successfully!")
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
