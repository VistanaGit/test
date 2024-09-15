
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database connection
# DATABASE_URL = "postgresql+psycopg2://amdb_user:bkk2ZKn3eESLEoojzTNpJwWDR67eqcBo@dpg-crjenqe8ii6s73fffvjg-a:5432/amdb"
DATABASE_URL = postgresql://amdb_user:bkk2ZKn3eESLEoojzTNpJwWDR67eqcBo@dpg-crjenqe8ii6s73fffvjg-a/amdb

# Create engine
engine = create_engine(DATABASE_URL)

# Create base class for models
Base = declarative_base()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


