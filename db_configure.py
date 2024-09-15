from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Hardcoded example with correct port number
DATABASE_URL = "mysql+pymysql://rd_db_usr:rd_pass@db_host:3306/RD_DB_3"

# Create engine
engine = create_engine(DATABASE_URL)

# Create base class for models
Base = declarative_base()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

