import os
import json
from typing import Optional, List, Dict, Any
from ai_engine.rag.retriever import KnowledgeRetriever

class AssessmentAgent:
    def __init__(self):
        self.retriever = KnowledgeRetriever()
        self.api_key = os.getenv("NVIDIA_NIM_API_KEY", "")
        self.base_url = os.getenv("NVIDIA_NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")
        self.model = "meta/llama-3.1-8b-instruct"
        self.used_questions = {}
    
    async def generate_diagnostic_question(self, topic: str, level: float) -> Dict[str, Any]:
        context = self.retriever.get_context(topic, level)
        
        prompt = f"""Generate ONE diagnostic question for a student learning "{topic}".
Student estimated level: {level}/10

Context:
{context}

Requirements:
- Multiple choice with 4 options (A, B, C, D)
- Should test foundational understanding
- Include the correct answer
- Format as JSON: {{"question": "...", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], "answer": "A", "concept_tested": "..."}}

JSON Output:"""
        
        return await self._call_llm_for_question(prompt)
    
    async def generate_question(
        self, 
        topic: str, 
        level: float, 
        purpose: str = "practice",
        misconceptions: Optional[List[str]] = None,
        avoid: Optional[str] = None
    ) -> Dict[str, Any]:
        context = self.retriever.get_context(topic, level)
        
        misconception_text = ""
        if misconceptions:
            misconception_text = f"Target these misconceptions: {', '.join(misconceptions)}"
        
        avoid_text = ""
        if avoid:
            avoid_text = f"Do NOT ask: {avoid[:100]}"
        
        prompt = f"""Generate ONE practice question for "{topic}" at level {level}/10.
Purpose: {purpose}
{misconception_text}
{avoid_text}

Context:
{context}

Requirements:
- Multiple choice with 4 options
- Match the difficulty level ({level}/10)
- Include correct answer and brief explanation
- Format as JSON: {{"question": "...", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], "answer": "A", "explanation": "..."}}

JSON Output:"""
        
        return await self._call_llm_for_question(prompt)
    
    async def _call_llm_for_question(self, prompt: str) -> Dict[str, Any]:
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
                        {"role": "system", "content": "You generate educational assessment questions. Always return valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 500
                },
                timeout=30.0
            )
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            try:
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                return json.loads(content.strip())
            except:
                return {
                    "question": content[:200],
                    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                    "answer": "A",
                    "explanation": "Please review the concept."
                }