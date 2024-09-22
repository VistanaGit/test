from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from db_configure import SessionLocal
from db_initialize import Account, Camera, Counter, ROI, Visitor

# Initialize FastAPI application
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # we can change this to the specific domains as we want to allow
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints
@app.get("/account_list")
def get_account_list(db: Session = Depends(get_db)):
    accounts = db.query(Account).all()
    return accounts

@app.get("/camera_list")
def get_camera_list(db: Session = Depends(get_db)):
    cameras = db.query(Camera).all()
    return cameras

@app.get("/counter_list")
def get_counter_list(db: Session = Depends(get_db)):
    counters = db.query(Counter).all()
    return counters

@app.get("/roi_list")
def get_roi_list(db: Session = Depends(get_db)):
    rois = db.query(ROI).all()
    return rois

@app.get("/visitor_list")
def get_visitor_list(db: Session = Depends(get_db)):
    visitors = db.query(Visitor).all()
    return visitors
