from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Ensure backend package can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.api import analyze

app = FastAPI(title="CogniEase API")

# Setup CORS to allow the frontend to interact with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the frontend's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/api", tags=["analyze"])

@app.get("/")
def read_root():
    return {"message": "Welcome to CogniEase API"}
