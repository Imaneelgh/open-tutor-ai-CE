# backend/open_tutorai/routers/quizzes.py
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

router = APIRouter()

# Stockage temporaire (remplacez par une DB en production)
quizzes_db: List[dict] = []

class QuestionCreate(BaseModel):
    text: str
    question_type: str = "multiple_choice"
    options: List[str] = []
    correct_answer: int | str
    points: int = 1
    explanation: Optional[str] = None

class QuizCreate(BaseModel):
    title: str
    description: Optional[str] = None
    subject: str
    questions: List[QuestionCreate]
    time_limit_minutes: Optional[int] = None
    is_active: bool = True

class QuizResponse(QuizCreate):
    id: str
    created_by: str
    created_at: str
    questions: List[dict]

# Stub auth (adaptez avec votre vrai système)
async def get_current_user(request: Request):
    # Vérifie le token/cookie ici si nécessaire
    return {"id": "teacher_demo", "role": "teacher", "name": "Enseignant Démo"}

@router.get("/", response_model=List[QuizResponse], tags=["quizzes"])
async def list_quizzes(current_user: dict = Depends(get_current_user)):
    # Normaliser les données pour le frontend étudiant
    result = []
    for q in quizzes_db:
        normalized = dict(q)
        normalized["questions"] = [
            {**qu, "correct_answer": int(qu["correct_answer"]) if str(qu["correct_answer"]).isdigit() else qu["correct_answer"]}
            for qu in normalized["questions"]
        ]
        result.append(normalized)
    return result

@router.post("/", response_model=QuizResponse, status_code=201, tags=["quizzes"])
async def create_quiz(
    quiz: QuizCreate,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    new_quiz = {
        "id": str(uuid.uuid4()),
        "title": quiz.title,
        "description": quiz.description,
        "subject": quiz.subject,
        "questions": [q.model_dump() for q in quiz.questions],
        "time_limit_minutes": quiz.time_limit_minutes,
        "is_active": quiz.is_active,
        "created_by": current_user["id"],
        "created_at": datetime.now().isoformat()
    }
    quizzes_db.append(new_quiz)
    return new_quiz
