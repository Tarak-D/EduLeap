from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.core.database import get_db
from app.models.student import Student, Session as LearningSession, Interaction
from ai_engine.orchestrator import AdaptiveLearningOrchestrator

router = APIRouter(prefix="/api/tutoring", tags=["tutoring"])

class StartSessionRequest(BaseModel):
    student_id: int
    topic: str
    name: Optional[str] = None

class AnswerRequest(BaseModel):
    session_id: int
    answer: str

class TutoringResponse(BaseModel):
    type: str  # diagnostic, explanation, question, analysis
    content: str
    options: Optional[List[str]] = None
    progress: Optional[dict] = None

orchestrator = AdaptiveLearningOrchestrator()

@router.post("/start", response_model=TutoringResponse)
async def start_session(req: StartSessionRequest, db: Session = Depends(get_db)):
    # Create/get student
    student = db.query(Student).filter(Student.id == req.student_id).first()
    if not student:
        student = Student(id=req.student_id, name=req.name, current_level=3.0)
        db.add(student)
        db.commit()
        db.refresh(student)
    
    # Create session
    session = LearningSession(
        student_id=student.id,
        topic=req.topic,
        current_concept=req.topic,
        learner_profile={"level": student.current_level, "misconceptions": []}
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Start diagnostic
    result = await orchestrator.start_diagnostic(session.id, req.topic, student.current_level)
    
    # Save interaction
    interaction = Interaction(
        session_id=session.id,
        interaction_type="diagnostic",
        content=result["content"]
    )
    db.add(interaction)
    db.commit()
    
    return TutoringResponse(
        type="diagnostic",
        content=result["content"],
        options=result.get("options"),
        progress={"session_id": session.id, "stage": "diagnostic"}
    )

@router.post("/answer", response_model=TutoringResponse)
async def submit_answer(req: AnswerRequest, db: Session = Depends(get_db)):
    session = db.query(LearningSession).filter(LearningSession.id == req.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get last interaction
    last_interaction = db.query(Interaction).filter(
        Interaction.session_id == session.id
    ).order_by(Interaction.timestamp.desc()).first()
    
    # Process through orchestrator
    result = await orchestrator.process_response(
        session_id=session.id,
        student_answer=req.answer,
        last_question=last_interaction.content if last_interaction else "",
        current_profile=session.learner_profile,
        topic=session.topic
    )
    
    # Save interaction
    interaction = Interaction(
        session_id=session.id,
        interaction_type=result["type"],
        content=result["content"],
        student_response=req.answer,
        evaluation=result.get("analysis")
    )
    db.add(interaction)
    
    # Update session profile
    if "updated_profile" in result:
        session.learner_profile = result["updated_profile"]
        # Update student level
        student = db.query(Student).filter(Student.id == session.student_id).first()
        student.current_level = result["updated_profile"].get("level", student.current_level)
    
    db.commit()
    
    return TutoringResponse(
        type=result["type"],
        content=result["content"],
        options=result.get("options"),
        progress=result.get("progress")
    )

@router.get("/session/{session_id}/history")
async def get_history(session_id: int, db: Session = Depends(get_db)):
    interactions = db.query(Interaction).filter(
        Interaction.session_id == session_id
    ).order_by(Interaction.timestamp.asc()).all()
    
    return {
        "interactions": [
            {
                "type": i.interaction_type,
                "content": i.content,
                "response": i.student_response,
                "evaluation": i.evaluation,
                "timestamp": i.timestamp
            }
            for i in interactions
        ]
    }