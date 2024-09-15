
# Step 3: Create the Tables Using db_configure.py
# In the main application file or an initialization script, you can create the tables using the Base and engine from db_configure.py.


from db_configure import engine, Base
import models  # Ensure the models are imported so that Base has all model definitions

# Create all tables
Base.metadata.create_all(bind=engine)