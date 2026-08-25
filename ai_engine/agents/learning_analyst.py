import os
import json
from typing import Dict, Any

class LearningAnalyst:
    def __init__(self):
        self.api_key = os.getenv("NVIDIA_NIM_API_KEY", "")
        self.base_url = os.getenv("NVIDIA_NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")
        self.model = "meta/llama-3.1-8b-instruct"
    
    async def evaluate_diagnostic_response(
        self, 
        question: str, 
        answer: str, 
        topic: str, 
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        prompt = f"""Analyze this diagnostic response:

Topic: {topic}
Question: {question}
Student Answer: {answer}
Current estimated level: {profile.get('level', 3.0)}/10

Evaluate and return JSON:
{{
    "estimated_level": float (1-10),
    "misconceptions": [list of identified misconceptions],
    "gaps": [list of prerequisite concepts the student seems to be missing],
    "confidence": float (0-1)
}}

JSON:"""
        
        return await self._analyze(prompt, profile)
    
    async def evaluate_response(
        self, 
        question: str, 
        answer: str, 
        topic: str, 
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        prompt = f"""Evaluate this student response:

Topic: {topic}
Question: {question}
Student Answer: {answer}
Current level: {profile.get('level', 3.0)}/10
Known misconceptions: {profile.get('misconceptions', [])}

Evaluate and return JSON:
{{
    "correct": boolean,
    "feedback": "Brief encouraging or corrective feedback (1-2 sentences)",
    "misconception": "identified misconception or null",
    "struggling": boolean (true if this seems like repeated difficulty),
    "updated_level": float (adjust slightly up or down based on performance),
    "recommended_action": "continue | reteach_prerequisite | simplify"
}}

JSON:"""
        
        return await self._analyze(prompt, profile)
    
    async def _analyze(self, prompt: str, profile: Dict[str, Any]) -> Dict[str, Any]:
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
                        {"role": "system", "content": "You are an expert learning analyst. Return only valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 400
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
                parsed = json.loads(content.strip())
                
                # Safety: don't let LLM crash the level
                if "updated_level" in parsed:
                    parsed["updated_level"] = max(1.0, min(10.0, float(parsed["updated_level"])))
                if "estimated_level" in parsed:
                    parsed["estimated_level"] = max(1.0, min(10.0, float(parsed["estimated_level"])))
                
                return parsed
            
            except Exception:
                return {
                    "correct": False,
                    "feedback": "Let's keep practicing!",
                    "misconception": None,
                    "struggling": False,
                    "updated_level": profile.get("level", 3.0),  # preserve current level!
                    "recommended_action": "continue"
                }