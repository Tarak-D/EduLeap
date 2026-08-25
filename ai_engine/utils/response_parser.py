import json
import re

class ResponseParser:
    """Parse structured outputs from LLM responses."""
    
    @staticmethod
    def extract_json(text: str) -> dict:
        """Extract JSON from markdown or raw text."""
        if not text:
            return {}
        
        # Try markdown code blocks
        patterns = [
            r'```json\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1).strip())
                except:
                    continue
        
        # Try raw JSON
        try:
            return json.loads(text.strip())
        except:
            pass
        
        # Try finding JSON object in text
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
        
        return {}
    
    @staticmethod
    def clean_explanation(text: str) -> str:
        """Clean up tutor explanations."""
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Ensure it ends with encouragement if missing
        if not any(word in text.lower()[-50:] for word in ['great', 'good job', 'well done', 'you can', 'keep', 'excellent']):
            text += "\n\nYou've got this! Keep practicing! 🌟"
        return text.strip()

response_parser = ResponseParser()