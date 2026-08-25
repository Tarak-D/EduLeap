import json
import os
from typing import Dict, Any, Optional
from ai_engine.agents.tutor_agent import TutorAgent
from ai_engine.agents.assessment_agent import AssessmentAgent
from ai_engine.agents.learning_analyst import LearningAnalyst
from ai_engine.rag.retriever import KnowledgeRetriever

class AdaptiveLearningOrchestrator:
    def __init__(self):
        self.tutor = TutorAgent()
        self.assessor = AssessmentAgent()
        self.analyst = LearningAnalyst()
        self.retriever = KnowledgeRetriever()
        self.diagnostic_count = {}  # session_id -> count
        self.stage = {}  # session_id -> current_stage
    
    async def start_diagnostic(self, session_id: int, topic: str, current_level: float) -> Dict[str, Any]:
        self.diagnostic_count[session_id] = 0
        self.stage[session_id] = "diagnostic"
        
        # Get diagnostic question from assessment agent
        question = await self.assessor.generate_diagnostic_question(topic, current_level)
        
        return {
            "type": "diagnostic",
            "content": question["question"],
            "options": question.get("options"),
            "expected_answer": question.get("answer")
        }
    
    async def process_response(
        self,
        session_id: int,
        student_answer: str,
        last_question: str,
        current_profile: Dict[str, Any],
        topic: str
    ) -> Dict[str, Any]:
        
        current_stage = self.stage.get(session_id, "diagnostic")
        
        # === STAGE 1: DIAGNOSTIC ===
        if current_stage == "diagnostic":
            self.diagnostic_count[session_id] = self.diagnostic_count.get(session_id, 0) + 1
            
            # Analyze the diagnostic response
            analysis = await self.analyst.evaluate_diagnostic_response(
                question=last_question,
                answer=student_answer,
                topic=topic,
                profile=current_profile
            )
            
            # After 3 diagnostic questions, move to teaching
            if self.diagnostic_count[session_id] >= 3:
                self.stage[session_id] = "teaching"
                
                # Determine level and gaps from all diagnostics
                updated_profile = {
                    "level": analysis.get("estimated_level", current_profile.get("level", 3.0)),
                    "misconceptions": analysis.get("misconceptions", []),
                    "gaps": analysis.get("gaps", []),
                    "topic": topic
                }
                
                # If gap detected, teach prerequisite first
                if updated_profile["gaps"]:
                    gap = updated_profile["gaps"][0]
                    explanation = await self.tutor.explain_prerequisite(
                        topic=topic,
                        prerequisite=gap,
                        level=updated_profile["level"]
                    )
                    
                    self.stage[session_id] = "gap_teaching"
                    
                    return {
                        "type": "explanation",
                        "content": explanation,
                        "updated_profile": updated_profile,
                        "progress": {"stage": "gap_teaching", "target": gap}
                    }
                
                # No gap - teach main topic
                explanation = await self.tutor.explain_concept(
                    topic=topic,
                    level=updated_profile["level"],
                    misconceptions=updated_profile["misconceptions"]
                )
                
                return {
                    "type": "explanation",
                    "content": explanation,
                    "updated_profile": updated_profile,
                    "progress": {"stage": "teaching", "topic": topic}
                }
            
            # More diagnostic questions needed
            next_q = await self.assessor.generate_diagnostic_question(
                topic, 
                analysis.get("estimated_level", current_profile.get("level", 3.0))
            )
            
            return {
                "type": "diagnostic",
                "content": next_q["question"],
                "options": next_q.get("options"),
                "analysis": analysis
            }
        
        # === STAGE 2: GAP TEACHING ===
        elif current_stage == "gap_teaching":
            # After teaching prerequisite, assess understanding
            self.stage[session_id] = "gap_assessment"
            question = await self.assessor.generate_question(
                topic=current_profile.get("gaps", [topic])[0],
                level=current_profile.get("level", 3.0),
                purpose="check_prerequisite"
            )
            
            return {
                "type": "question",
                "content": question["question"],
                "options": question.get("options")
            }
        
        # === STAGE 3: TEACHING ===
        elif current_stage == "teaching":
            # After explanation, give practice question
            self.stage[session_id] = "assessment"
            question = await self.assessor.generate_question(
                topic=topic,
                level=current_profile.get("level", 3.0),
                purpose="practice",
                misconceptions=current_profile.get("misconceptions", [])
            )
            
            return {
                "type": "question",
                "content": question["question"],
                "options": question.get("options")
            }
        
        # === STAGE 4: ASSESSMENT / ADAPTATION ===
        elif current_stage in ["assessment", "gap_assessment"]:
            analysis = await self.analyst.evaluate_response(
                question=last_question,
                answer=student_answer,
                topic=topic,
                profile=current_profile
            )
            
            updated_profile = current_profile.copy()
            updated_profile["level"] = analysis.get("updated_level", current_profile.get("level"))
            
            # If struggling with same misconception repeatedly
            if analysis.get("struggling", False) and analysis.get("misconception"):
                # Switch teaching strategy
                explanation = await self.tutor.explain_concept(
                    topic=topic if current_stage == "assessment" else current_profile.get("gaps", [topic])[0],
                    level=max(updated_profile["level"] - 1, 1),
                    misconceptions=[analysis["misconception"]],
                    strategy="simplify"  # Break into simpler parts
                )
                
                self.stage[session_id] = "reteach"
                
                return {
                    "type": "explanation",
                    "content": explanation,
                    "updated_profile": updated_profile,
                    "analysis": analysis,
                    "progress": {"stage": "reteach", "reason": "misconception_detected"}
                }
            
            # Success - move to next concept or harder question
            if analysis.get("correct", False):
                updated_profile["level"] = min(updated_profile["level"] + 0.5, 10)
                
                # Generate next question (harder)
                next_q = await self.assessor.generate_question(
                    topic=topic,
                    level=updated_profile["level"],
                    purpose="advance"
                )
                
                self.stage[session_id] = "assessment"
                
                return {
                    "type": "question",
                    "content": f"✅ Great! {analysis.get('feedback', '')}\n\nNow try this:\n\n{next_q['question']}",
                    "options": next_q.get("options"),
                    "updated_profile": updated_profile,
                    "analysis": analysis,
                    "progress": {"stage": "assessment", "level": updated_profile["level"]}
                }
            
            # Wrong but not struggling - try similar difficulty
            else:
                next_q = await self.assessor.generate_question(
                    topic=topic,
                    level=updated_profile["level"],
                    purpose="practice",
                    avoid=last_question
                )
                
                self.stage[session_id] = "assessment"
                
                return {
                    "type": "question",
                    "content": f"❌ {analysis.get('feedback', 'Let\'s try another one.')}\n\n{next_q['question']}",
                    "options": next_q.get("options"),
                    "updated_profile": updated_profile,
                    "analysis": analysis
                }
        
        # === STAGE 5: RETEACH ===
        elif current_stage == "reteach":
            # After reteaching, assess again
            self.stage[session_id] = "assessment"
            question = await self.assessor.generate_question(
                topic=topic,
                level=current_profile.get("level", 3.0),
                purpose="check_understanding"
            )
            
            return {
                "type": "question",
                "content": question["question"],
                "options": question.get("options")
            }
        
        # Fallback
        return {
            "type": "explanation",
            "content": "Let's continue learning! What would you like to explore next?"
        }