from db_configure import SessionLocal
from models import Account, UserStatusEnum

def insert_records():
    session = SessionLocal()
    try:
        # Define records with Iranian names using UserStatusEnum for user_status
        accounts = [
            Account(user_id=1001, user_name='ahmad_hosseini', password='password123', first_name='Ahmad', last_name='Hosseini', tel='09123456789', user_photo='ahmad_hosseini.jpg', user_status=UserStatusEnum.active),
            Account(user_id=1002, user_name='reza_shokouhi', password='password456', first_name='Reza', last_name='Shokouhi', tel='09234567890', user_photo='reza_shokouhi.jpg', user_status=UserStatusEnum.inactive),
            Account(user_id=1003, user_name='fatemeh_ghasemi', password='password789', first_name='Fatemeh', last_name='Ghasemi', tel='09345678901', user_photo='fatemeh_ghasemi.jpg', user_status=UserStatusEnum.active),
            Account(user_id=1004, user_name='mehdi_rahimi', password='password012', first_name='Mehdi', last_name='Rahimi', tel='09456789012', user_photo='mehdi_rahimi.jpg', user_status=UserStatusEnum.inactive),
            Account(user_id=1005, user_name='leila_mohammadi', password='password345', first_name='Leila', last_name='Mohammadi', tel='09567890123', user_photo='leila_mohammadi.jpg', user_status=UserStatusEnum.active)
        ]
        
        # Add records to the session
        session.add_all(accounts)
        session.commit()
        print("Records inserted successfully!")
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    insert_records()
