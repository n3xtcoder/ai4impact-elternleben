from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import uuid
from datetime import datetime
# Database setup
DATABASE_URL = "sqlite:///./mock_api.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

# ------------- Database Models -------------

class Webinar(Base):
    __tablename__ = "webinars"
    uuid = Column(String, primary_key=True, index=True)
    host_id = Column(String, index=True)
    topic = Column(String)
    start_time = Column(String)  # ISO 8601 format
    duration = Column(Integer)
    agenda = Column(String, nullable=True)
    join_url = Column(String, nullable=True)
    status = Column(String, nullable=True)

class WebinarRegistrant(Base):
    __tablename__ = "webinar_registrants"
    uuid = Column(String, primary_key=True, index=True)
    webinar_id = Column(String, index=True)
    name = Column(String)
    email = Column(String)

class Expert(Base):
    __tablename__ = "experts"
    uuid = Column(String, primary_key=True, index=True)
    name = Column(String)
    specialty = Column(String)
    is_available = Column(Boolean, default=True)
    zoom_host_id = Column(String, nullable=True)

class Appointment(Base):
    __tablename__ = "appointments"
    uuid = Column(String, primary_key=True, index=True)
    expert_id = Column(String, index=True)
    service = Column(String, index=True)
    datetime = Column(String)  # Format: YYYY-MM-DD HH:MM
    client_name = Column(String, nullable=True)
    client_email = Column(String, nullable=True)
    client_phone = Column(String, nullable=True)
    is_booked = Column(Boolean, default=False)
    status = Column(String, nullable=True)

# Create tables in the database
Base.metadata.create_all(bind=engine)

# ------------- Request Models -------------

# Zoom Webinar Models
class WebinarResponse(BaseModel):
    uuid: str
    host_id: str
    topic: str
    type: int
    start_time: str  # ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
    duration: int
    timezone: str
    created_at: str
    agenda: Optional[str] = None
    join_url: Optional[str] = None

class WebinarRegistrantCreateRequest(BaseModel):
    email: str
    first_name: str
    last_name: Optional[str] = None

class WebinarRegistrantResponse(BaseModel):
    uuid: str
    email: str
    first_name: str
    last_name: Optional[str] = None
    create_time: str
    status: str

# SimplyBook.me Models
class ExpertResponse(BaseModel):
    uuid: str
    name: str
    is_available: bool

class AvailableSlot(BaseModel):
    start_datetime: str
    end_datetime: str

class AppointmentCreateRequest(BaseModel):
    client_name: str
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    service: str
    expert_id: str

class AppointmentResponse(BaseModel):
    uuid: str
    client_name: str
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    service: str
    expert_id: str
    datetime: str  # Format: YYYY-MM-DD HH:MM
    status: Optional[str] = None

class AppointmentUpdateRequest(BaseModel):
    datetime: Optional[str] = None  # Format: YYYY-MM-DD HH:MM
    service: Optional[str] = None
    status: Optional[str] = None

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------- Zoom Webinar API (Mock) -------------

@app.get("/webinars", response_model=List[WebinarResponse])
def get_all_webinars(db: Session = Depends(get_db)):
    webinars = db.query(Webinar).all()
    # Mimic Zoom's response structure
    response = [
        {
            "uuid": str(uuid.uuid4()),
            "host_id": webinar.host_id,
            "topic": webinar.topic,
            "type": 5,  # Webinar type
            "start_time": webinar.start_time,
            "duration": webinar.duration,
            "timezone": "UTC",
            "created_at": "2025-01-01T00:00:00Z",
            "agenda": webinar.agenda,
            "join_url": webinar.join_url
        }
        for webinar in webinars
    ]
    return response

@app.post("/webinars/{webinar_id}/registrants", response_model=WebinarRegistrantResponse)
def create_webinar_registration(webinar_id: str, request: WebinarRegistrantCreateRequest, db: Session = Depends(get_db)):
    registrant_id = str(uuid.uuid4())
    registrant = WebinarRegistrant(
        uuid=registrant_id,
        webinar_id=webinar_id,
        name=f"{request.first_name} {request.last_name or ''}".strip(),
        email=request.email
    )
    db.add(registrant)
    db.commit()
    db.refresh(registrant)
    # Mimic Zoom's response structure
    response = {
        "uuid": registrant.uuid,
        "email": registrant.email,
        "first_name": request.first_name,
        "last_name": request.last_name,
        "create_time": "2025-01-01T00:00:00Z",
        "status": "approved"
    }
    return response

@app.get("/webinars/{webinar_id}/registrants", response_model=List[WebinarRegistrantResponse])
def get_webinar_registrants(webinar_id: str, db: Session = Depends(get_db)):
    registrants = db.query(WebinarRegistrant).filter(WebinarRegistrant.webinar_id == webinar_id).all()
    # Mimic Zoom's response structure
    response = [
        {
            "uuid": registrant.uuid,
            "email": registrant.email,
            "first_name": registrant.name.split()[0],
            "last_name": " ".join(registrant.name.split()[1:]) if len(registrant.name.split()) > 1 else "",
            "create_time": "2025-01-01T00:00:00Z",
            "status": "approved"
        }
        for registrant in registrants
    ]
    return response

@app.patch("/webinars/{webinar_id}/registrants/{registrant_id}", response_model=WebinarRegistrantResponse)
def update_webinar_registration(webinar_id: str, registrant_id: str, request: WebinarRegistrantCreateRequest, db: Session = Depends(get_db)):
    registrant = db.query(WebinarRegistrant).filter(
        WebinarRegistrant.uuid == registrant_id,
        WebinarRegistrant.webinar_id == webinar_id
    ).first()
    if not registrant:
        raise HTTPException(status_code=404, detail="Registrant not found")

    registrant.name = f"{request.first_name} {request.last_name or ''}".strip()
    registrant.email = request.email
    db.commit()
    db.refresh(registrant)
    # Mimic Zoom's response structure
    response = {
        "uuid": registrant.uuid,
        "email": registrant.email,
        "first_name": request.first_name,
        "last_name": request.last_name,
        "create_time": "2025-01-01T00:00:00Z",
        "status": "approved"
    }
    return response

# ------------- SimplyBook.me Endpoints -------------

@app.get("/experts", response_model=List[ExpertResponse])
def get_all_experts(db: Session = Depends(get_db)):
    """
    Get a list of all experts regardless of availability status.
    """
    experts = db.query(Expert).all()
    response = [{"uuid": expert.uuid, "name": expert.name, "is_available": expert.is_available} for expert in experts]
    return response


@app.get("/experts/available", response_model=List[ExpertResponse])
def get_available_experts(db: Session = Depends(get_db)):
    experts = db.query(Expert).filter(Expert.is_available == True).all()
    response = [{"uuid": expert.uuid, "name": expert.name, "is_available": expert.is_available} for expert in experts]
    return response


@app.get("/experts/{expert_id}/available-slots", response_model=List[AvailableSlot])
def get_available_slots(expert_id: str):
    return [
        {"start_datetime": "2025-03-06T10:00:00Z", "end_datetime": "2025-03-06T10:30:00Z"},
        {"start_datetime": "2025-03-06T12:00:00Z", "end_datetime": "2025-03-06T12:30:00Z"},
        {"start_datetime": "2025-03-06T14:00:00Z", "end_datetime": "2025-03-06T14:30:00Z"},
    ]


@app.post("/bookings/new", response_model=AppointmentResponse)
def book_appointment(request: AppointmentCreateRequest, db: Session = Depends(get_db)):
    appointment_id = str(uuid.uuid4())
    appointment_datetime = datetime.now().strftime("%Y-%m-%d %H:%M")
    appointment = Appointment(
        uuid=appointment_id,
        client_name=request.client_name,
        client_email=request.client_email,
        client_phone=request.client_phone,
        service=request.service,
        expert_id=request.expert_id,
        datetime=appointment_datetime,
        status="confirmed"  # Default status for new appointments
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@app.patch("/bookings/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(appointment_id: str, request: AppointmentUpdateRequest, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.uuid == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment.datetime = datetime.now().strftime("%Y-%m-%d %H:%M"),
    if request.service:
        appointment.service = request.service
    if request.status:
        appointment.status = request.status

    db.commit()
    db.refresh(appointment)
    return appointment


@app.delete("/bookings/{appointment_id}")
def cancel_appointment(appointment_id: str, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.uuid == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    db.delete(appointment)
    db.commit()
    return {"message": "Appointment cancelled successfully"}

@app.get("/")
def welcome_page():
    return {
        "message": "Welcome to the N3XTCODER x ElternLeben Mock API Service",
        "version": "0.0.1",
        "available_endpoints": {
            "webinars": {
                "GET /webinars": "Get list of all webinars",
                "GET /experts/{expert_id}/webinars": "Get list of webinars for a specific expert",
                "POST /experts/{expert_id}/webinars": "Create a new webinar for an expert",
                "POST /webinars/{webinar_id}/registrants": "Register for a webinar",
                "GET /webinars/{webinar_id}/registrants": "Get webinar registrants",
                "PATCH /webinars/{webinar_id}/registrants/{registrant_id}": "Update webinar registration"
            },
            "experts": {
                "GET /experts": "Get list of all experts",
                "GET /experts/available": "Get list of available experts",
                "GET /experts/{expert_id}/available-slots": "Get available time slots for an expert"
            },
            "appointments": {
                "POST /bookings/new": "Create a new appointment",
                "PATCH /bookings/{appointment_id}": "Update an existing appointment",
                "DELETE /bookings/{appointment_id}": "Cancel an appointment"
            }
        },
        "documentation": "/docs",
        "openapi": "/openapi.json"
    }

# Add new endpoint to create a webinar for an expert
class WebinarCreateRequest(BaseModel):
    topic: str
    start_time: str  # ISO 8601 format
    duration: int
    agenda: Optional[str] = None

@app.post("/experts/{expert_id}/webinars", response_model=WebinarResponse)
def create_expert_webinar(
    expert_id: str, 
    request: WebinarCreateRequest, 
    db: Session = Depends(get_db)
):
    # Check if expert exists
    expert = db.query(Expert).filter(Expert.uuid == expert_id).first()
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    
    # Create new webinar
    webinar_id = str(uuid.uuid4())
    webinar = Webinar(
        uuid=webinar_id,
        host_id=expert.uuid,  # Use expert ID as host ID
        topic=request.topic,
        start_time=request.start_time,
        duration=request.duration,
        agenda=request.agenda,
        join_url=f"https://zoom.us/j/{webinar_id}",  # Mock join URL
        status="scheduled"  # Default status for new webinars
    )
    
    db.add(webinar)
    db.commit()
    db.refresh(webinar)
    
    # Return in Zoom format
    return {
        "uuid": str(uuid.uuid4()),
        "host_id": webinar.host_id,
        "topic": webinar.topic,
        "type": 5,
        "start_time": webinar.start_time,
        "duration": webinar.duration,
        "timezone": "UTC",
        "created_at": "2025-01-01T00:00:00Z",
        "agenda": webinar.agenda,
        "join_url": webinar.join_url
    }

@app.get("/experts/{expert_id}/webinars", response_model=List[WebinarResponse])
def get_expert_webinars(expert_id: str, db: Session = Depends(get_db)):
    # Check if expert exists
    expert = db.query(Expert).filter(Expert.uuid == expert_id).first()
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    
    # Get all webinars for this expert
    webinars = db.query(Webinar).filter(Webinar.host_id == expert_id).all()
    
    return [
        {
            "uuid": str(uuid.uuid4()),
            "host_id": webinar.host_id,
            "topic": webinar.topic,
            "type": 5,
            "start_time": webinar.start_time,
            "duration": webinar.duration,
            "timezone": "UTC",
            "created_at": "2025-01-01T00:00:00Z",
            "agenda": webinar.agenda,
            "join_url": webinar.join_url
        }
        for webinar in webinars
    ]
