from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.student import Interaction, Session as LearningSession, Student

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/session/{session_id}")
async def session_analytics(session_id: int, db: Session = Depends(get_db)):
    interactions = db.query(Interaction).filter(Interaction.session_id == session_id).all()
    
    total = len(interactions)
    correct = sum(1 for i in interactions if i.evaluation and i.evaluation.get("correct"))
    diagnostic = sum(1 for i in interactions if i.interaction_type == "diagnostic")
    
    return {
        "session_id": session_id,
        "total_interactions": total,
        "correct_answers": correct,
        "diagnostic_questions": diagnostic,
        "accuracy": round(correct / max(total - diagnostic, 1), 2),
        "interactions": [
            {"type": i.interaction_type, "has_response": bool(i.student_response), "evaluation": i.evaluation}
            for i in interactions
        ]
    }

@router.get("/student/{student_id}/progress")
async def student_progress(student_id: int, db: Session = Depends(get_db)):
    sessions = db.query(LearningSession).filter(LearningSession.student_id == student_id).all()
    student = db.query(Student).filter(Student.id == student_id).first()
    
    return {
        "student_id": student_id,
        "current_level": student.current_level if student else 3.0,
        "total_sessions": len(sessions),
        "topics_covered": list(set(s.topic for s in sessions)),
        "session_history": [
            {"id": s.id, "topic": s.topic, "status": s.status, "profile": s.learner_profile}
            for s in sessions
        ]
    }