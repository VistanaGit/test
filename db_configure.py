from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database connection
DATABASE_URL = "postgresql+psycopg2://amuser:ampass@localhost:5432/amdb"

# Create engine
try:
    engine = create_engine(DATABASE_URL)
    print("Database engine created successfully.")
except Exception as e:
    print(f"Error creating database engine: {e}")

# Create base class for models
try:
    Base = declarative_base()
    print("Base class for models created successfully.")
except Exception as e:
    print(f"Error creating base class for models: {e}")

# Create session factory
try:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    print("Session factory created successfully.")
except Exception as e:
    print(f"Error creating session factory: {e}")
