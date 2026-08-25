from sqlalchemy.orm import Session
from app.models.student import Student, KnowledgeGap

class StudentService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_gap(self, student_id: int, concept: str, prerequisite: str, severity: float = 1.0):
        gap = KnowledgeGap(
            student_id=student_id,
            concept=concept,
            prerequisite_gap=prerequisite,
            severity=severity
        )
        self.db.add(gap)
        self.db.commit()
        return gap
    
    def update_level(self, student_id: int, new_level: float):
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if student:
            student.current_level = max(1.0, min(10.0, new_level))
            self.db.commit()
        return student
    
    def get_or_create(self, student_id: int, name: str = None):
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            student = Student(id=student_id, name=name, current_level=3.0)
            self.db.add(student)
            self.db.commit()
            self.db.refresh(student)
        return student