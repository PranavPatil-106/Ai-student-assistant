from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import auth, faculty, student
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI(title="AI-Powered Student Learning Assistant")

# CORS middleware for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(faculty.router, prefix="/faculty", tags=["Faculty"])
app.include_router(student.router, prefix="/student", tags=["Student"])

@app.get("/")
async def root():
    return {"message": "AI-Powered Student Learning Assistant API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)