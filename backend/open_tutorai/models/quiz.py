from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"

class Question(BaseModel):
    id: Optional[str] = None
    text: str
    question_type: QuestionType
    options: List[str] = []  # Pour multiple_choice/true_false
    correct_answer: str  # Index ou texte selon le type
    points: int = 1
    explanation: Optional[str] = None

class Quiz(BaseModel):
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    subject: str
    questions: List[Question]
    time_limit_minutes: Optional[int] = None
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class QuizSubmission(BaseModel):
    quiz_id: str
    user_id: str
    answers: dict  # {question_id: user_answer}
    score: Optional[float] = None
    completed_at: datetime = Field(default_factory=datetime.utcnow)
