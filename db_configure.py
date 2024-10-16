from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database connection
DATABASE_URL = "postgresql://rddb_user:wrUGaO8sbjbrHmkb1aReMIpLs94YSRJ8@dpg-cs7n3gtumphs73a9khhg-a/rddb_fwzi"

# Create engine
engine = create_engine(DATABASE_URL)
print("Database engine created successfully.")


# Create base class for models
Base = declarative_base()
print("Base class for models created successfully.")


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
print("Session factory created successfully.")
