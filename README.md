<div align="center">

# 🎓 EduLeap

### AI-Powered Adaptive Learning Platform

<p><strong>Personalized tutoring powered by AI. Adapts to every learner's strengths, gaps, and learning pace.</strong></p>

<p>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=white" alt="React">
  <img src="https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square" alt="Status">
</p>

<p>
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-api-overview">API</a> •
  <a href="#-documentation">Documentation</a>
</p>

</div>

---

## 🎯 What is EduLeap?

**EduLeap** is an intelligent tutoring platform that personalizes education through AI.

Instead of providing the same content and difficulty level to every learner, EduLeap continuously analyzes student performance and adapts the learning experience to their current proficiency, strengths, weaknesses, and pace.

### EduLeap:

- 🧠 **Diagnoses** student understanding through assessments
- 🎯 **Adapts** explanations to the learner's proficiency level
- ❓ **Generates** follow-up questions to reinforce concepts
- 📊 **Tracks** learning progress and performance
- 🔍 **Identifies** knowledge gaps
- 🛤️ **Personalizes** the learning path based on performance
- 📚 **Grounds** AI responses using a retrieval-based knowledge base

The platform combines a modern **React frontend**, **FastAPI backend**, **AI orchestration layer**, **PostgreSQL**, and **ChromaDB** to provide an adaptive learning experience.

---

## ✨ Key Features

### 🧑‍🎓 Adaptive Learning

- Diagnostic learning assessments
- Learner proficiency estimation
- Personalized explanations
- Dynamic practice questions
- Adaptive learning paths
- Continuous learner-profile updates

### 🤖 AI-Powered Tutoring

- Adaptive AI tutoring conversations
- Context-aware responses
- Personalized explanation generation
- Automated answer evaluation
- Learning-gap detection
- Follow-up question generation

### 📚 Retrieval-Augmented Generation

- Knowledge-base integration
- Document retrieval
- Semantic search
- ChromaDB vector storage
- Retrieval-grounded AI responses

### 📊 Learning Analytics

- Student progress tracking
- Session history
- Performance analysis
- Knowledge-gap identification
- Learner profile updates

### 🔐 User Experience

- Guest-based onboarding
- Student learning sessions
- Interactive tutoring interface
- Progress dashboard
- Session-based learning

### 🏗️ Engineering

- Modular architecture
- RESTful APIs
- AI orchestration layer
- PostgreSQL persistence
- Automated testing
- Docker-based deployment

---

## 🏗️ Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                        React UI                             │
│              Student Interface & Dashboard                 │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ REST API
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                         │
│                                                             │
│  Authentication │ Sessions │ Tutoring │ Analytics APIs     │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                        AI Engine                            │
│                                                             │
│  Orchestrator │ Tutoring Agents │ Assessment │ Evaluation │
└───────────────────────┬───────────────────┬─────────────────┘
                        │                   │
                        ▼                   ▼
             ┌──────────────────┐  ┌────────────────────────┐
             │    PostgreSQL    │  │       ChromaDB         │
             │                  │  │                        │
             │ • Student Data   │  │ • Embeddings           │
             │ • Sessions       │  │ • Knowledge Base       │
             │ • Progress       │  │ • Semantic Retrieval   │
             │ • Learning State │  │ • RAG Context          │
             └──────────────────┘  └───────────┬────────────┘
                                               │
                                               ▼
                                    ┌────────────────────────┐
                                    │    Knowledge Base       │
                                    │                        │
                                    │ • Learning Content     │
                                    │ • Documents             │
                                    │ • Reference Material   │
                                    └────────────────────────┘
```

### Architecture Components

| Component | Technology | Purpose |
|---|---|---|
| **Frontend** | React, JavaScript | Student-facing chat and dashboard |
| **Backend** | FastAPI, SQLAlchemy, Pydantic | Authentication, tutoring, sessions, and analytics APIs |
| **AI Engine** | Python, NVIDIA NIM | AI orchestration, tutoring, assessment, and evaluation |
| **Database** | PostgreSQL | Persistent student, session, and learning data |
| **Vector Search** | ChromaDB | Knowledge retrieval and semantic search |
| **Testing** | Pytest | Automated application and AI testing |
| **Deployment** | Docker, Docker Compose | Containerized development and deployment |

---

## 📁 Project Structure

```text
EduLeap/
│
├── frontend/                    # React application
│   ├── src/
│   ├── public/
│   └── package.json
│
├── backend/                     # FastAPI service
│   ├── app/
│   ├── tests/
│   └── requirements.txt
│
├── ai_engine/                   # AI orchestration layer
│   ├── agents/
│   ├── rag/
│   ├── prompts/
│   └── orchestrator.py
│
├── docs/                        # Architecture and API documentation
│   ├── architecture.md
│   ├── api_spec.md
│   └── demo_script.md
│
├── data/                        # Sample knowledge base
│
├── deployment/                  # Deployment configurations
│
├── Makefile                     # Helper commands
├── .env.example                 # Environment variable template
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

Make sure the following are installed:

```text
Python 3.10+
Node.js 18+
PostgreSQL 15+
Git
NVIDIA NIM API key or compatible LLM
```

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/Tarak-D/EduLeap.git
cd EduLeap
```

#### 2. Set Up Environment Variables

Copy the environment template:

```bash
cp .env.example .env
```

Update `.env` with your configuration:

```env
NVIDIA_NIM_API_KEY=your_key_here
NVIDIA_NIM_BASE_URL=https://integrate.api.nvidia.com/v1

DATABASE_URL=postgresql://eduleap:eduleap123@localhost:5432/eduleap_db

CHROMA_HOST=localhost
CHROMA_PORT=8001

SECRET_KEY=your-secret-key
```

> ⚠️ **Security:** Never commit your actual API keys, passwords, or secrets to GitHub.

#### 3. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### 4. Install Frontend Dependencies

```bash
cd ../frontend
npm install
```

#### 5. Start the Backend

Open Terminal 1:

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Backend:

```text
http://localhost:8000
```

FastAPI Swagger documentation:

```text
http://localhost:8000/docs
```

#### 6. Start the Frontend

Open Terminal 2:

```bash
cd frontend
npm start
```

Frontend:

```text
http://localhost:3000
```

---

## ⚡ Makefile Shortcuts

If the project is configured with the provided `Makefile`, you can use:

```bash
make setup
make backend
make frontend
make dev
```

---

## 📡 API Overview

| Endpoint | Method | Purpose |
|---|:---:|---|
| `/api/auth/guest` | `POST` | Guest authentication |
| `/api/tutoring/start` | `POST` | Start a tutoring session |
| `/api/tutoring/answer` | `POST` | Submit an answer and receive feedback |
| `/api/students/{id}` | `GET` | Retrieve student profile |
| `/api/analytics/progress` | `GET` | Retrieve learning analytics |

### Interactive API Documentation

Once the backend is running, open:

```text
http://localhost:8000/docs
```

FastAPI provides interactive Swagger/OpenAPI documentation automatically.

Detailed project API documentation:

[API Specification](docs/api_spec.md)

---

## 🧠 How It Works

EduLeap follows a continuous adaptive learning loop:

```text
1. Student starts a session on a topic
                    │
                    ▼
2. AI runs a diagnostic assessment
                    │
                    ▼
3. Learner's current proficiency is estimated
                    │
                    ▼
4. Tutor generates a personalized explanation
                    │
                    ▼
5. Follow-up practice questions are generated
                    │
                    ▼
6. Student responses are evaluated
                    │
                    ▼
7. Learning gaps are identified
                    │
                    ▼
8. Learner profile is updated
                    │
                    └──────────────► Next Session
```

### Learning Cycle

**Assess → Understand → Explain → Practice → Evaluate → Adapt**

This feedback loop allows the platform to continuously adjust the learning experience according to student performance.

---

## 📚 Retrieval-Augmented Generation (RAG)

EduLeap uses **Retrieval-Augmented Generation (RAG)** to provide knowledge-grounded AI responses.

```text
Learning Content
       │
       ▼
Document Processing
       │
       ▼
Chunking
       │
       ▼
Embedding Generation
       │
       ▼
     ChromaDB
       │
       ▼
Semantic Retrieval
       │
       ▼
Relevant Knowledge Context
       │
       ▼
AI Tutor / LLM
       │
       ▼
Grounded Explanation
```

### Why RAG?

RAG allows the AI tutor to retrieve relevant learning material before generating a response, helping keep explanations aligned with the available educational knowledge base.

---

## 🛠️ Tech Stack

### Frontend

- React 18
- JavaScript
- Tailwind CSS

### Backend

- Python 3.10+
- FastAPI
- SQLAlchemy
- Pydantic

### AI / ML

- Python
- NVIDIA NIM
- OpenAI-compatible models
- AI orchestration
- Agentic AI
- Retrieval-Augmented Generation

### Database & Search

- PostgreSQL
- ChromaDB
- Vector embeddings

### Testing

- Pytest

### Deployment

- Docker
- Docker Compose

### Development

- Git
- GitHub
- Make

---

## 🧪 Testing

Run the complete test suite:

```bash
pytest
```

Run tests with detailed output:

```bash
pytest -v
```

---

## 📖 Documentation

Project documentation is maintained in the `docs/` directory:

- 📐 [System Architecture](docs/architecture.md)
- 📡 [API Specification](docs/api_spec.md)
- 🎬 [Demo Script](docs/demo_script.md)

---

## 🎓 Skills Demonstrated

### Software Engineering

- Full-stack web development
- REST API development
- Database design
- Modular application architecture
- API design and documentation

### Artificial Intelligence

- Generative AI
- Agentic AI
- AI orchestration
- Adaptive tutoring
- Automated assessment
- Personalized content generation

### Machine Learning & Data

- Learning analytics
- Knowledge-gap detection
- Semantic search
- Vector databases
- Retrieval-Augmented Generation

### Engineering & Deployment

- Docker
- Docker Compose
- Automated testing
- Environment configuration
- Git/GitHub workflows

---

## 🗺️ Future Roadmap

- [ ] Improved adaptive difficulty tuning
- [ ] Multi-language support
- [ ] Teacher dashboard
- [ ] Administrator dashboard
- [ ] Advanced student performance modeling
- [ ] Enhanced curriculum grounding
- [ ] Real-time collaborative tutoring
- [ ] Expanded learning analytics
- [ ] Support for additional subjects and learning domains

---

## 🤝 Contributing

Contributions are welcome!

### Development Workflow

1. Fork the repository
2. Create a feature branch:

```bash
git checkout -b feature/amazing-feature
```

3. Make your changes
4. Run the test suite:

```bash
pytest
```

5. Commit your changes:

```bash
git commit -m "Add amazing feature"
```

6. Push the branch:

```bash
git push origin feature/amazing-feature
```

7. Open a Pull Request

---

## 📝 License

This project is maintained for educational and experimental purposes.

See the [LICENSE](LICENSE) file for details.

---

<div align="center">

### 🎓 EduLeap

**AI-powered personalized learning for every learner.**

Made with ❤️ for personalized learning.

⭐ If you find this project useful, consider giving the repository a star!

</div>
