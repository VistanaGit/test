from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database connection
DATABASE_URL = "postgresql://rddb_pjzg_user:TSqli96RCceWMtFX7KexhDTgWSBTMkXF@dpg-ct7c0hqj1k6c73b67ln0-a/rddb_pjzg"

# Create engine
engine = create_engine(DATABASE_URL)
print("Database engine created successfully.")


# Create base class for models
Base = declarative_base()
print("Base class for models created successfully.")


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
print("Session factory created successfully.")
