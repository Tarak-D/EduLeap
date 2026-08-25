import os
from typing import List, Optional
from ai_engine.rag.retriever import KnowledgeRetriever

class TutorAgent:
    def __init__(self):
        self.retriever = KnowledgeRetriever()
        self.api_key = os.getenv("NVIDIA_NIM_API_KEY", "")
        self.base_url = os.getenv("NVIDIA_NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")
        # NVIDIA NIM model - Llama 3.1 8B (fast, good for tutoring)
        self.model = "meta/llama-3.1-8b-instruct"
    
    async def explain_concept(
        self, 
        topic: str, 
        level: float, 
        misconceptions: Optional[List[str]] = None,
        strategy: str = "standard"
    ) -> str:
        context = self.retriever.get_context(topic, level)
        prompt = self._build_explanation_prompt(topic, level, context, misconceptions, strategy)
        
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are EduLeap, an adaptive AI tutor for children. Use simple language, examples, and encouragement. Keep explanations concise and friendly."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 800
                },
                timeout=30.0
            )
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    async def explain_prerequisite(self, topic: str, prerequisite: str, level: float) -> str:
        context = self.retriever.get_context(prerequisite, max(level - 1, 1))
        
        prompt = f"""Explain the prerequisite concept "{prerequisite}" which is needed to understand "{topic}".
        
Student level: {level}/10 (simplified explanation needed)
Context from knowledge base:
{context}

Instructions:
- Use very simple language suitable for a child
- Use visual/concrete examples (like pizza, apples, etc. for fractions)
- Keep it under 200 words
- End with encouragement

Explanation:"""
        
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a patient, encouraging tutor for children."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 600
                },
                timeout=30.0
            )
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    def _build_explanation_prompt(
        self, 
        topic: str, 
        level: float, 
        context: str, 
        misconceptions: Optional[List[str]],
        strategy: str
    ) -> str:
        strategy_instruction = ""
        if strategy == "simplify":
            strategy_instruction = "BREAK THIS INTO 2-3 VERY SIMPLE STEPS. Use the simplest possible explanation."
        
        misconception_warning = ""
        if misconceptions:
            misconception_warning = f"Watch out for these common mistakes: {', '.join(misconceptions)}. Address them gently."
        
        return f"""Explain the concept: "{topic}"

Student level: {level}/10
Strategy: {strategy}
{strategy_instruction}
{misconception_warning}

Knowledge base context:
{context}

Instructions:
- Use age-appropriate language
- Include 1 concrete example
- Keep under 250 words
- Use encouraging tone
- If strategy is 'simplify', break into numbered steps

Explanation:"""