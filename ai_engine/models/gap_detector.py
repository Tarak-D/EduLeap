class GapDetector:
    """Detect knowledge gaps based on response patterns."""
    
    PREREQUISITE_MAP = {
        "fraction addition": ["common denominators", "equivalent fractions", "basic division"],
        "common denominators": ["multiplication tables", "factors", "equivalent fractions"],
        "equivalent fractions": ["multiplication tables", "division"],
        "simplifying fractions": ["greatest common divisor", "division"],
    }
    
    def detect(self, topic: str, misconception: str, history: list) -> list:
        """
        Return list of prerequisite gaps based on topic and misconception.
        """
        gaps = []
        
        # Map misconception to likely prerequisite gap
        if "denominator" in misconception.lower() or "add" in misconception.lower():
            gaps.append("common denominators")
        
        if "equivalent" in misconception.lower():
            gaps.append("equivalent fractions")
        
        if "simplify" in misconception.lower() or "reduce" in misconception.lower():
            gaps.append("greatest common divisor")
        
        # Add topic-specific prerequisites
        topic_lower = topic.lower()
        for key, prereqs in self.PREREQUISITE_MAP.items():
            if key in topic_lower:
                for p in prereqs:
                    if p not in gaps:
                        gaps.append(p)
        
        return gaps

gap_detector = GapDetector()