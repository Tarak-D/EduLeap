import numpy as np

class LevelEstimator:
    """Heuristic-based learner level estimation."""
    
    def __init__(self):
        self.weights = {
            "correct_streak": 0.3,
            "response_time": 0.1,  # placeholder
            "difficulty_history": 0.4,
            "gap_severity": 0.2
        }
    
    def estimate(self, interactions: list) -> float:
        """
        Simple heuristic: 
        - Start at 3.0
        - +0.5 for each correct answer streak
        - -1.0 for each identified gap
        - Cap between 1 and 10
        """
        if not interactions:
            return 3.0
        
        level = 3.0
        streak = 0
        
        for interaction in interactions:
            eval_data = interaction.get("evaluation", {}) or {}
            
            if eval_data.get("correct"):
                streak += 1
                if streak >= 2:
                    level += 0.5
            else:
                streak = 0
                level -= 0.3
            
            # Penalize for gaps
            if eval_data.get("misconception"):
                level -= 0.5
        
        return max(1.0, min(10.0, level))
    
    def adjust_from_gap(self, current_level: float, gap_severity: float) -> float:
        """Lower level if significant gap detected."""
        adjustment = gap_severity * 1.5
        return max(1.0, current_level - adjustment)

level_estimator = LevelEstimator()