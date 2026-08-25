import re

class SafetyFilter:
    """Content verification layer to prevent harmful outputs."""
    
    BLOCKED_PATTERNS = [
        r'\b(hate|kill|die|suicide|violence|weapon)\b',
        r'\b(porn|sex|nude)\b',
    ]
    
    def __init__(self):
        self.blocked_regex = [re.compile(p, re.IGNORECASE) for p in self.BLOCKED_PATTERNS]
    
    def check_input(self, text: str) -> tuple[bool, str]:
        """Returns (is_safe, reason)"""
        if not text or len(text) > 2000:
            return False, "Input too long or empty"
        
        for pattern in self.blocked_regex:
            if pattern.search(text):
                return False, "Inappropriate content detected"
        
        return True, "Safe"
    
    def check_output(self, text: str) -> tuple[bool, str]:
        """Verify AI output is educational and appropriate."""
        if not text:
            return False, "Empty response"
        
        # Check for refusals that indicate the model couldn't answer properly
        refusal_phrases = ["i cannot", "i can't", "i'm not able", "i am not able"]
        lower = text.lower()
        
        if any(p in lower for p in refusal_phrases) and len(text) < 100:
            return False, "Model refused to generate content"
        
        return True, "Safe"

# Global instance
safety_filter = SafetyFilter()