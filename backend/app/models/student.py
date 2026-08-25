from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    current_level = Column(Float, default=3.0)  # 1-10 scale
    created_at = Column(DateTime, default=datetime.utcnow)
    
    sessions = relationship("Session", back_populates="student")
    gaps = relationship("KnowledgeGap", back_populates="student")

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    topic = Column(String)
    current_concept = Column(String)
    status = Column(String, default="active")  # active, completed, paused
    learner_profile = Column(JSON, default=dict)  # persistent profile
    created_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("Student", back_populates="sessions")
    interactions = relationship("Interaction", back_populates="session")

class Interaction(Base):
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    interaction_type = Column(String)  # diagnostic, tutor, assessment, analysis
    content = Column(Text)  # question/explanation
    student_response = Column(Text, nullable=True)
    evaluation = Column(JSON, nullable=True)  # analyst result
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("Session", back_populates="interactions")

class KnowledgeGap(Base):
    __tablename__ = "knowledge_gaps"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    concept = Column(String)  # e.g., "fraction_addition"
    prerequisite_gap = Column(String)  # e.g., "common_denominators"
    severity = Column(Float, default=1.0)  # 0-1
    detected_at = Column(DateTime, default=datetime.utcnow)
    resolved = Column(String, default="open")  # open, resolved
    
    student = relationship("Student", back_populates="gaps")