from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./health_monitor.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Endpoint(Base):
    __tablename__ = "endpoints"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    interval_mins = Column(Integer, default=5)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    logs = relationship("PingLog", back_populates="endpoint", cascade="all, delete")


class PingLog(Base):
    __tablename__ = "ping_logs"
    id = Column(Integer, primary_key=True, index=True)
    endpoint_id = Column(Integer, ForeignKey("endpoints.id"), nullable=False)
    status_code = Column(Integer, nullable=True)
    response_ms = Column(Float, nullable=True)
    is_up = Column(Boolean, nullable=False)
    error_msg = Column(String, nullable=True)
    checked_at = Column(DateTime, default=datetime.utcnow)
    endpoint = relationship("Endpoint", back_populates="logs")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)