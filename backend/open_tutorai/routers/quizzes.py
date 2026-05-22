# backend/open_tutorai/routers/quizzes.py

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
import json
import csv
from io import StringIO

router = APIRouter(prefix="/api/v1/quizzes", tags=["quizzes"])

# =============================================================================
# DONNÉES MOCK (Simule la base de données pour le développement)
# =============================================================================
quizzes_db: List[dict] = [
    {
        "id": "quiz_algo_001",
        "title": "Quiz Algorithmique Fondamentale",
        "description": "Testez vos connaissances sur les structures de données, la complexité et les algorithmes classiques.",
        "subject": "Algorithmique",
        "time_limit_minutes": 15,
        "is_active": True,
        "created_by": "system",
        "created_at": datetime.now().isoformat(),
        "questions": [
            {"id": "q1", "text": "Que signifie le sigle IA ?", "question_type": "multiple_choice", "options": ["Intelligence Artificielle", "Interface Automatique", "Internet Avancé"], "correct_answer": "0", "points": 1, "explanation": "IA = Intelligence Artificielle"},
            {"id": "q2", "text": "Quelle notation décrit la complexité dans le pire des cas ?", "question_type": "multiple_choice", "options": ["Notation Omega (Ω)", "Notation Theta (Θ)", "Notation Big O (O)", "Notation Sigma (Σ)"], "correct_answer": "2", "points": 1, "explanation": "La notation Big O (O) décrit la borne supérieure de la complexité."},
            {"id": "q3", "text": "Quelle structure fonctionne selon le principe LIFO ?", "question_type": "multiple_choice", "options": ["File (Queue)", "Tableau (Array)", "Pile (Stack)", "Liste chaînée"], "correct_answer": "2", "points": 1, "explanation": "La Pile (Stack) suit le principe LIFO."},
            {"id": "q4", "text": "Quelle est la complexité moyenne du QuickSort ?", "question_type": "multiple_choice", "options": ["O(n)", "O(n log n)", "O(n²)", "O(log n)"], "correct_answer": "1", "points": 1, "explanation": "O(n log n) est la complexité moyenne."},
            {"id": "q5", "text": "La recherche dichotomique nécessite un tableau trié.", "question_type": "true_false", "options": ["Vrai", "Faux"], "correct_answer": "0", "points": 1, "explanation": "Correct, elle nécessite un tableau trié."},
            {"id": "q6", "text": "Qu'est-ce qu'une fonction récursive ?", "question_type": "multiple_choice", "options": ["Une fonction qui s'appelle elle-même", "Une fonction sans paramètres", "Une fonction qui retourne 0", "Une fonction infinie"], "correct_answer": "0", "points": 1, "explanation": "La récursivité est l'appel de la fonction par elle-même."},
            {"id": "q7", "text": "Quel algorithme trouve le plus court chemin (sans poids négatifs) ?", "question_type": "multiple_choice", "options": ["Dijkstra", "Prim", "Kruskal", "BFS"], "correct_answer": "0", "points": 1, "explanation": "L'algorithme de Dijkstra est utilisé pour les plus courts chemins."},
            {"id": "q8", "text": "La programmation dynamique stocke les résultats intermédiaires.", "question_type": "true_false", "options": ["Vrai", "Faux"], "correct_answer": "0", "points": 1, "explanation": "C'est le principe de la mémoïsation."},
            {"id": "q9", "text": "Quelle est la complexité d'un tableau de taille n ?", "question_type": "multiple_choice", "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"], "correct_answer": "2", "points": 1, "explanation": "L'espace mémoire est linéaire O(n)."},
            {"id": "q10", "text": "Que mesure la complexité algorithmique ?", "question_type": "multiple_choice", "options": ["Le temps et l'espace", "Le nombre de lignes", "La difficulté", "Le langage"], "correct_answer": "0", "points": 1, "explanation": "Elle mesure les ressources (temps/mémoire)."}
        ]
    }
]

# =============================================================================
# MODÈLES PYDANTIC
# =============================================================================

class QuestionCreate(BaseModel):
    text: str
    question_type: str = "multiple_choice"
    options: List[str] = []
    correct_answer: str  # Stocké en string (index "0", "1", etc.)
    points: int = 1
    explanation: Optional[str] = None

class QuizCreate(BaseModel):
    title: str
    description: Optional[str] = None
    subject: str
    time_limit_minutes: Optional[int] = 15
    is_active: bool = True
    questions: List[QuestionCreate]

class QuizResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    subject: str
    time_limit_minutes: Optional[int]
    is_active: bool
    questions: List[dict] # On retourne les questions telles quelles

class QuizSubmission(BaseModel):
    user_id: str
    answers: dict # {question_id: answer_index_string}

class QuizResult(BaseModel):
    submission_id: str
    quiz_id: str
    user_id: str
    score: float
    total_questions: int
    correct_answers: int
    feedback: str

# =============================================================================
# AUTH STUB
# =============================================================================
async def get_current_user(request: Request):
    # Retourne un utilisateur fictif pour le développement
    return {"id": "user_demo", "role": "student", "name": "Étudiant Démo"}

# =============================================================================
# ROUTES STANDARD
# =============================================================================

@router.get("/", response_model=List[dict])
async def list_quizzes(current_user: dict = Depends(get_current_user)):
    """Lister tous les quiz actifs"""
    return [q for q in quizzes_db if q.get("is_active", True)]

@router.get("/{quiz_id}", response_model=dict)
async def get_quiz(quiz_id: str):
    """Récupérer un quiz par ID"""
    quiz = next((q for q in quizzes_db if q["id"] == quiz_id), None)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz introuvable")
    return quiz

@router.post("/", response_model=dict, status_code=201)
async def create_quiz(
    quiz: QuizCreate,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Créer un nouveau quiz (Enseignant/Admin uniquement)"""
    if current_user.get("role") not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Permission refusée")
    
    new_quiz = {
        "id": str(uuid.uuid4()),
        "title": quiz.title,
        "description": quiz.description,
        "subject": quiz.subject,
        "time_limit_minutes": quiz.time_limit_minutes,
        "is_active": quiz.is_active,
        "created_by": current_user.get("id", "unknown"),
        "created_at": datetime.now().isoformat(),
        "questions": [q.model_dump() for q in quiz.questions]
    }
    quizzes_db.append(new_quiz)
    return new_quiz

# =============================================================================
# ROUTES DE SOUMISSION & SCORING
# =============================================================================

@router.post("/{quiz_id}/submit", response_model=QuizResult)
async def submit_quiz(quiz_id: str, payload: QuizSubmission):
    """Soumettre un quiz et calculer le score"""
    quiz = next((q for q in quizzes_db if q["id"] == quiz_id), None)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz introuvable")
    
    questions = quiz["questions"]
    correct_count = 0
    
    for q in questions:
        user_answer = str(payload.answers.get(q["id"], "")).strip()
        correct_answer = str(q["correct_answer"]).strip()
        
        if user_answer == correct_answer:
            correct_count += 1
            
    total = len(questions)
    score = round((correct_count / total) * 100, 2) if total > 0 else 0
    
    feedback = "Parfait ! 🌟" if score == 100 else "Bon travail ! 👍" if score >= 50 else "Continuez à pratiquer ! 💪"
    
    return QuizResult(
        submission_id=str(uuid.uuid4()),
        quiz_id=quiz_id,
        user_id=payload.user_id,
        score=score,
        total_questions=total,
        correct_answers=correct_count,
        feedback=feedback
    )

# =============================================================================
# ROUTES D'IMPORT (SPRINT 2)
# =============================================================================

@router.post("/import/json")
async def import_quiz_json(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """Importer un quiz depuis un fichier JSON"""
    if current_user.get("role") not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Permission refusée")
        
    try:
        content = await file.read()
        data = json.loads(content)
        
        # Validation basique
        if "title" not in data or "questions" not in data:
            raise HTTPException(status_code=400, detail="Format JSON invalide: champs 'title' et 'questions' requis")
            
        # Création du quiz
        new_quiz = {
            "id": str(uuid.uuid4()),
            "title": data["title"],
            "description": data.get("description", ""),
            "subject": data.get("subject", "Import JSON"),
            "time_limit_minutes": data.get("time_limit_minutes", 15),
            "is_active": True,
            "created_by": current_user.get("id"),
            "created_at": datetime.now().isoformat(),
            "questions": data["questions"] # On suppose que le format est bon
        }
        quizzes_db.append(new_quiz)
        return {"message": "Quiz importé avec succès", "id": new_quiz["id"]}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Fichier JSON corrompu")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/import/template")
async def get_import_template():
    """Télécharger un modèle JSON pour l'import"""
    return {
        "title": "Mon Nouveau Quiz",
        "description": "Description du quiz",
        "subject": "Matière",
        "time_limit_minutes": 15,
        "questions": [
            {
                "text": "Question exemple ?",
                "options": ["Option A", "Option B", "Option C"],
                "correct_answer": "0", # Index de la bonne réponse
                "points": 1,
                "explanation": "Explication ici"
            }
        ]
    }
