from sqlalchemy import text
from db_configure import SessionLocal
from db_initialize import Visitor, ROI, Counter, Camera, Account  # Ensure Account is imported

def reset_tables():
    session = SessionLocal()
    try:
        # Delete records from the child tables first
        session.query(Visitor).delete()
        session.query(ROI).delete()
        session.query(Counter).delete()
        session.query(Camera).delete()
        session.query(Account).delete()  # Delete from Account last

        session.commit()
        print("All tables have been reset successfully!")
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    reset_tables()