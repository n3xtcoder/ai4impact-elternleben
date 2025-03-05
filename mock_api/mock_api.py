from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import uuid

# Database setup
DATABASE_URL = "sqlite:///./mock_api.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

# ------------- Database Models -------------

class Webinar(Base):
    __tablename__ = "webinars"
    id = Column(String, primary_key=True, index=True)
    host_id = Column(String, index=True)
    topic = Column(String)
    start_time = Column(String)  # ISO 8601 format
    duration = Column(Integer)
    agenda = Column(String, nullable=True)
    join_url = Column(String, nullable=True)

class WebinarRegistrant(Base):
    __tablename__ = "webinar_registrants"
    id = Column(String, primary_key=True, index=True)
    webinar_id = Column(String, index=True)
    name = Column(String)
    email = Column(String)

class Expert(Base):
    __tablename__ = "experts"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    is_available = Column(Boolean, default=True)

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(String, primary_key=True, index=True)
    client_name = Column(String)
    client_email = Column(String, nullable=True)
    client_phone = Column(String, nullable=True)
    service_id = Column(String, index=True)
    expert_id = Column(String)
    datetime = Column(String)  # Format: YYYY-MM-DD HH:MM
    status = Column(String, nullable=True)

# Create tables in the database
Base.metadata.create_all(bind=engine)

# ------------- Request Models -------------

# Zoom Webinar Models
class WebinarResponse(BaseModel):
    uuid: str
    id: int
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
    id: str
    email: str
    first_name: str
    last_name: Optional[str] = None
    create_time: str
    status: str

# SimplyBook.me Models
class ExpertResponse(BaseModel):
    id: str
    name: str
    is_available: bool

class AvailableSlot(BaseModel):
    start_datetime: str
    end_datetime: str

class AppointmentCreateRequest(BaseModel):
    client_name: str
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    service_id: str
    expert_id: str
    datetime: str  # Format: YYYY-MM-DD HH:MM

class AppointmentResponse(BaseModel):
    id: str
    client_name: str
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    service_id: str
    expert_id: str
    datetime: str  # Format: YYYY-MM-DD HH:MM
    status: Optional[str] = None

class AppointmentUpdateRequest(BaseModel):
    datetime: Optional[str] = None  # Format: YYYY-MM-DD HH:MM
    service_id: Optional[str] = None
    status: Optional[str] = None

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------- Zoom Webinar API (Mock) -------------

@app.get("/users/{user_id}/webinars", response_model=List[WebinarResponse])
def get_webinar_list(user_id: str, db: Session = Depends(get_db)):
    webinars = db.query(Webinar).filter(Webinar.host_id == user_id).all()
    # Mimic Zoom's response structure
    response = [
        {
            "uuid": str(uuid.uuid4()),
            "id": int(webinar.id),
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
        id=registrant_id,
        webinar_id=webinar_id,
        name=f"{request.first_name} {request.last_name or ''}".strip(),
        email=request.email
    )
    db.add(registrant)
    db.commit()
    db.refresh(registrant)
    # Mimic Zoom's response structure
    response = {
        "id": registrant.id,
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
            "id": registrant.id,
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
        WebinarRegistrant.id == registrant_id,
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
        "id": registrant.id,
        "email": registrant.email,
        "first_name": request.first_name,
        "last_name": request.last_name,
        "create_time": "2025-01-01T00:00:00Z",
        "status": "approved"
    }
    return response

@app.get("/experts/available", response_model=List[ExpertResponse])
def get_available_experts(db: Session = Depends(get_db)):
    experts = db.query(Expert).filter(Expert.is_available == True).all()
    response = [{"id": expert.id, "name": expert.name, "is_available": expert.is_available} for expert in experts]
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
    appointment = Appointment(
        id=appointment_id,
        client_name=request.client_name,
        client_email=request.client_email,
        client_phone=request.client_phone,
        service_id=request.service_id,
        expert_id=request.expert_id,
        datetime=request.datetime,
        status="confirmed"  # Default status for new appointments
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@app.patch("/bookings/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(appointment_id: str, request: AppointmentUpdateRequest, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if request.datetime:
        appointment.datetime = request.datetime
    if request.service_id:
        appointment.service_id = request.service_id
    if request.status:
        appointment.status = request.status

    db.commit()
    db.refresh(appointment)
    return appointment


@app.delete("/bookings/{appointment_id}")
def cancel_appointment(appointment_id: str, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    db.delete(appointment)
    db.commit()
    return {"message": "Appointment cancelled successfully"}