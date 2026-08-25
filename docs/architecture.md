# EduLeap Architecture

## System Overview
EduLeap uses an agentic AI architecture with three specialized agents coordinated by an orchestrator.

## Components

### Frontend (React)
- ChatInterface: Main student interaction
- LearningDashboard: Progress visualization
- TopicSelector: Topic browsing

### Backend (FastAPI)
- Auth API: Guest login, JWT tokens
- Tutoring API: Session management, adaptive loop
- Student API: Profile and gap management
- Analytics API: Progress tracking

### AI Engine
- Orchestrator: Manages Assess → Teach → Test → Analyze → Adapt loop
- TutorAgent: Generates personalized explanations via NVIDIA NIM
- AssessmentAgent: Creates diagnostic and practice questions
- LearningAnalyst: Evaluates responses, detects misconceptions
- RAG: ChromaDB vector store for curriculum grounding

### Data Flow
1. Student selects topic
2. Orchestrator runs 3-question diagnostic
3. Level estimated, gaps identified
4. TutorAgent explains at appropriate level
5. AssessmentAgent generates practice questions
6. LearningAnalyst evaluates and adapts
7. Profile updates persist across session

## NVIDIA NIM Integration
All LLM calls route through NVIDIA NIM API (OpenAI-compatible):
- Base URL: https://integrate.api.nvidia.com/v1
- Model: meta/llama-3.1-8b-instruct