from ai_engine.rag.vector_store import vector_store

class KnowledgeRetriever:
    def __init__(self):
        self.store = vector_store
    
    def get_context(self, topic: str, level: float) -> str:
        if self.store.available:
            try:
                level_range = self._get_level_range(level)
                results = self.store.query(
                    query_text=topic,
                    n_results=3,
                    filter_dict={"level": {"$gte": level_range[0], "$lte": level_range[1]}}
                )
                if results and results.get("documents"):
                    contexts = []
                    for doc_list in results["documents"]:
                        for doc in doc_list:
                            contexts.append(doc)
                    if contexts:
                        return "\n\n".join(contexts)
            except Exception:
                pass
        
        return self._get_fallback_context(topic)
    
    def _get_level_range(self, level: float):
        return [max(1, level - 1), min(10, level + 1)]
    
    def _get_fallback_context(self, topic: str) -> str:
        fallbacks = {
            "fraction addition": """Fraction Addition: To add fractions, they must have the same denominator (bottom number). If denominators differ, find a common denominator by finding the LCM or multiplying them. Example: 1/2 + 1/3 = 3/6 + 2/6 = 5/6. Common mistake: Adding numerators and denominators separately (1/2 + 1/3 ≠ 2/5).""",
            "common denominators": """Common Denominators: A common denominator is a number that both denominators can divide into evenly. For 1/2 and 1/3, common denominators include 6, 12, 18. The least common denominator (LCD) is 6. To convert: multiply numerator and denominator by the same number. 1/2 = 3/6 (multiply by 3), 1/3 = 2/6 (multiply by 2).""",
            "fractions": """Fractions represent parts of a whole. The top number is the numerator (parts you have). The bottom number is the denominator (total equal parts). Example: 1/2 means 1 part out of 2 equal parts.""",
            "equivalent fractions": """Equivalent fractions have the same value but different numerators and denominators. Found by multiplying/dividing both by same number. Example: 1/2 = 2/4 = 3/6. 2/3 = 4/6 = 6/9. Common mistakes: Only multiplying numerator. Thinking 1/2 and 2/5 are equivalent.""",
            "simplifying fractions": """Simplifying means reducing to lowest terms by dividing numerator and denominator by their GCD. Example: 4/8 simplifies to 1/2. 6/9 simplifies to 2/3. Common mistakes: Not dividing by the greatest common divisor. Stopping too early."""
        }
        
        for key, value in fallbacks.items():
            if key in topic.lower():
                return value
        
        return f"General information about {topic}."