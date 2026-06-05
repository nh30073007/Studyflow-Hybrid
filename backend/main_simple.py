from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.hybrid_manager import get_hybrid_manager
import uvicorn
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

hybrid_manager = get_hybrid_manager()

class AskRequest(BaseModel):
    user_id: str
    question: str

class AskResponse(BaseModel):
    answer: str
    user_id: str
    timestamp: str
    topic: str = None

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "StudyFlow AI API", "status": "active"}

@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    answer = await hybrid_manager.process_query(request.user_id, request.question)
    return AskResponse(
        answer=answer,
        user_id=request.user_id,
        timestamp=datetime.now().isoformat()
    )

@app.get("/progress/{user_id}")
async def progress(user_id: str):
    return {"user_id": user_id, "total_questions": 0, "message": "No data yet"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)