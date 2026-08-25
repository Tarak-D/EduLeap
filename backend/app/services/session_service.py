from sqlalchemy.orm import Session
from app.models.student import Session as LearningSession, Interaction

class SessionService:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, student_id: int, topic: str):
        session = LearningSession(
            student_id=student_id,
            topic=topic,
            current_concept=topic,
            learner_profile={"level": 3.0, "misconceptions": [], "gaps": []}
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def add_interaction(self, session_id: int, interaction_type: str, content: str, 
                       response: str = None, evaluation: dict = None):
        interaction = Interaction(
            session_id=session_id,
            interaction_type=interaction_type,
            content=content,
            student_response=response,
            evaluation=evaluation
        )
        self.db.add(interaction)
        self.db.commit()
        return interaction
    
    def update_profile(self, session_id: int, profile: dict):
        session = self.db.query(LearningSession).filter(LearningSession.id == session_id).first()
        if session:
            session.learner_profile = profile
            self.db.commit()
        return session