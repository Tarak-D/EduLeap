import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://eduleap:eduleap123@localhost:5432/eduleap_db")
    
    # NVIDIA NIM Configuration
    NVIDIA_NIM_API_KEY = os.getenv("NVIDIA_NIM_API_KEY", "")
    NVIDIA_NIM_BASE_URL = os.getenv("NVIDIA_NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")
    
    CHROMA_URL = os.getenv("CHROMA_URL", "http://localhost:8001")
    SECRET_KEY = os.getenv("SECRET_KEY", "eduleap-hackathon-secret-2026")

settings = Settings()