from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base, SessionLocal
from app.api import tutoring, auth, student, analytics

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="EduLeap API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(student.router)
app.include_router(tutoring.router)
app.include_router(analytics.router)

@app.get("/health")
async def health():
    return {"status": "ok", "project": "EduLeap", "llm_provider": "nvidia_nim"}

@app.on_event("startup")
async def startup():
    from app.core.seed_data import seed_demo_data
    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()