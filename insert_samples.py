from db_configure import SessionLocal
from db_initialize import Account, Camera, Counter, ROI, Visitor
from datetime import datetime

# Insert accounts data
def insert_accounts():
    session = SessionLocal()
    try:
        accounts = [
            Account(user_id=1001, user_name='ahmad_hosseini', password='password123', first_name='Ahmad', last_name='Hosseini', tel='09123456789', user_photo='ahmad_hosseini.jpg', user_status='active'),
            Account(user_id=1002, user_name='reza_shokouhi', password='password456', first_name='Reza', last_name='Shokouhi', tel='09234567890', user_photo='reza_shokouhi.jpg', user_status='active'),
            Account(user_id=1003, user_name='fatemeh_ghasemi', password='password789', first_name='Fatemeh', last_name='Ghasemi', tel='09345678901', user_photo='fatemeh_ghasemi.jpg', user_status='active'),
            Account(user_id=1004, user_name='mehdi_rahimi', password='password012', first_name='Mehdi', last_name='Rahimi', tel='09456789012', user_photo='mehdi_rahimi.jpg', user_status='inactive'),
            Account(user_id=1005, user_name='leila_mohammadi', password='password345', first_name='Leila', last_name='Mohammadi', tel='09567890123', user_photo='leila_mohammadi.jpg', user_status='active')
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
            ROI(roi_id=1, counter_roi_id=1, roi_coor='[0,0,100,100]', roi_desc='Region 1 for Counter 1'),
            ROI(roi_id=2, counter_roi_id=1, roi_coor='[101,0,200,100]', roi_desc='Region 2 for Counter 1'),
            ROI(roi_id=3, counter_roi_id=2, roi_coor='[0,0,100,100]', roi_desc='Region 1 for Counter 2'),
            ROI(roi_id=4, counter_roi_id=2, roi_coor='[101,0,200,100]', roi_desc='Region 2 for Counter 2'),
            ROI(roi_id=5, counter_roi_id=3, roi_coor='[0,0,100,100]', roi_desc='Region 1 for Counter 3')
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
            Visitor(person_id=1, roi_id=1, counter_id=1, cam_id=1, person_duration_in_roi=120, person_age_group='young', person_gender='male', persons_count=3, current_datetime=datetime(2024, 9, 19, 10, 0, 0)),
            Visitor(person_id=2, roi_id=2, counter_id=1, cam_id=1, person_duration_in_roi=150, person_age_group='adult', person_gender='female', persons_count=2, current_datetime=datetime(2024, 9, 19, 11, 0, 0)),
            Visitor(person_id=3, roi_id=3, counter_id=2, cam_id=2, person_duration_in_roi=90, person_age_group='teenager', person_gender='male', persons_count=1, current_datetime=datetime(2024, 9, 19, 12, 0, 0)),
            Visitor(person_id=4, roi_id=4, counter_id=2, cam_id=2, person_duration_in_roi=110, person_age_group='young', person_gender='female', persons_count=4, current_datetime=datetime(2024, 9, 19, 13, 0, 0)),
            Visitor(person_id=5, roi_id=5, counter_id=3, cam_id=3, person_duration_in_roi=200, person_age_group='senior', person_gender='male', persons_count=5, current_datetime=datetime(2024, 9, 19, 14, 0, 0))
        ]
        session.add_all(visitors)
        session.commit()
        print("Visitors inserted successfully!")
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        session.close()

# Main function to run all insert operations
def main():
    insert_accounts()
    insert_cameras()
    insert_counters()
    insert_rois()
    insert_visitors()

if __name__ == "__main__":
    main()
