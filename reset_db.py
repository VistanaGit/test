from db_configure import engine
from db_initialize import Base
from sqlalchemy import inspect

# Function to list all existing tables
def list_tables():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()  # Retrieves the list of table names
    if existing_tables:
        print("Existing tables:")
        for table in existing_tables:
            print(f"- {table}")
    else:
        print("No tables found.")

# Function to drop all tables
def drop_all_tables():
    list_tables()  # List tables before dropping
    Base.metadata.drop_all(bind=engine)
    print("All tables have been dropped.")

if __name__ == "__main__":
    drop_all_tables()
