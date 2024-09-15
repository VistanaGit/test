from db_configure import engine, Base
import models  # Ensure the models are imported so that Base has all model definitions

def initialize_db():
    # Drop all tables if they exist
    Base.metadata.drop_all(bind=engine)
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    initialize_db()

