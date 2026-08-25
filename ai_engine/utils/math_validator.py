from fractions import Fraction
import re

class MathValidator:
    """Validate math answers with actual computation, not LLM guessing."""
    
    @staticmethod
    def normalize_fraction(text: str) -> str:
        """Extract fraction from text like 'A) 3/4' or '3/4'."""
        match = re.search(r'(\d+)\s*/\s*(\d+)', text)
        if match:
            return f"{match.group(1)}/{match.group(2)}"
        # Handle decimals
        match = re.search(r'(\d+\.?\d*)', text)
        if match:
            return match.group(1)
        return text.strip()
    
    @staticmethod
    def check_fraction_addition(question: str, student_answer: str, expected: str = None) -> dict:
        """Actually compute fraction addition to validate."""
        try:
            # Extract fractions from question (naive but works for demo)
            nums = re.findall(r'(\d+)\s*/\s*(\d+)', question)
            if len(nums) >= 2:
                a = Fraction(int(nums[0][0]), int(nums[0][1]))
                b = Fraction(int(nums[1][0]), int(nums[1][1]))
                correct_val = a + b
                
                # Parse student answer
                student_str = MathValidator.normalize_fraction(student_answer)
                student_frac = Fraction(student_str)
                
                is_correct = (student_frac == correct_val)
                
                return {
                    "correct": is_correct,
                    "correct_answer": str(correct_val),
                    "student_parsed": str(student_frac),
                    "method": "computed"
                }
        except Exception as e:
            return {"correct": False, "error": str(e), "method": "failed"}
        
        return {"correct": False, "method": "unparseable"}
    
    @staticmethod
    def validate(question: str, student_answer: str, topic: str) -> dict:
        if "fraction" in topic.lower() and ("add" in question.lower() or "+" in question):
            return MathValidator.check_fraction_addition(question, student_answer)
        return {"correct": None, "method": "llm_fallback"}

math_validator = MathValidator()