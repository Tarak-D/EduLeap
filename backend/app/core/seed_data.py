from sqlalchemy.orm import Session
from app.models.student import Student

def seed_demo_data(db: Session):
    """Create demo student if none exists."""
    if db.query(Student).first():
        return
    
    demo = Student(id=1, name="Demo Student", current_level=3.0)
    db.add(demo)
    db.commit()