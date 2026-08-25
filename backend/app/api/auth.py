from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import create_access_token
from app.models.student import Student

router = APIRouter(prefix="/api/auth", tags=["auth"])

class GuestLoginRequest(BaseModel):
    name: str

@router.post("/guest")
async def guest_login(req: GuestLoginRequest, db: Session = Depends(get_db)):
    student = Student(name=req.name, current_level=3.0)
    db.add(student)
    db.commit()
    db.refresh(student)
    
    token = create_access_token({"sub": str(student.id), "name": student.name})
    return {"access_token": token, "student_id": student.id, "name": student.name}

@router.get("/me")
async def get_me(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"id": student.id, "name": student.name, "level": student.current_level}