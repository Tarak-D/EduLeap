from collections import defaultdict

class PerformanceTracker:
    """Track student performance patterns over time."""
    
    def __init__(self):
        self.concept_attempts = defaultdict(list)
        self.misconception_counts = defaultdict(int)
    
    def record_attempt(self, concept: str, correct: bool, misconception: str = None):
        self.concept_attempts[concept].append({
            "correct": correct,
            "misconception": misconception
        })
        
        if misconception:
            self.misconception_counts[misconception] += 1
    
    def is_struggling(self, concept: str, threshold: int = 2) -> bool:
        """Check if student has failed concept multiple times."""
        attempts = self.concept_attempts.get(concept, [])
        recent_wrong = sum(1 for a in attempts[-3:] if not a["correct"])
        return recent_wrong >= threshold
    
    def get_recurring_misconceptions(self, min_count: int = 2) -> list:
        """Return misconceptions that appear multiple times."""
        return [m for m, count in self.misconception_counts.items() if count >= min_count]
    
    def get_concept_accuracy(self, concept: str) -> float:
        attempts = self.concept_attempts.get(concept, [])
        if not attempts:
            return 0.0
        correct = sum(1 for a in attempts if a["correct"])
        return correct / len(attempts)

performance_tracker = PerformanceTracker()