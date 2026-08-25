from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.student import Student, KnowledgeGap

router = APIRouter(prefix="/api/students", tags=["students"])

@router.get("/{student_id}")
async def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {
        "id": student.id,
        "name": student.name,
        "current_level": student.current_level,
        "gaps": [
            {"concept": g.concept, "prerequisite_gap": g.prerequisite_gap, "severity": g.severity, "status": g.resolved}
            for g in student.gaps
        ]
    }

@router.get("/{student_id}/gaps")
async def get_gaps(student_id: int, db: Session = Depends(get_db)):
    gaps = db.query(KnowledgeGap).filter(
        KnowledgeGap.student_id == student_id,
        KnowledgeGap.resolved == "open"
    ).all()
    return {"gaps": [{"concept": g.concept, "prerequisite": g.prerequisite_gap, "severity": g.severity} for g in gaps]}