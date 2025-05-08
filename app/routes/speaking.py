from fastapi import APIRouter, Depends, HTTPException
from app.services.question_service import get_all_questions_by_part, add_question, get_all_questions
from app.models.schemas import QuestionRequest
from app.dependencies.auth import get_current_user, require_role

router = APIRouter(prefix="/api/speaking", tags=["speaking"])

@router.get("/part1")
async def get_part1_questions(current_user: dict = Depends(get_current_user)):
    return {"questions": get_all_questions_by_part("part1")}

@router.post("/part1", dependencies=[Depends(require_role("admin"))])
async def add_part1_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    add_question("part1", request.question)
    return {"message": "Question added successfully", "question": request.question}

@router.get("/part2")
async def get_part2_questions(current_user: dict = Depends(get_current_user)):
    return {"questions": get_all_questions_by_part("part2")}

@router.post("/part2", dependencies=[Depends(require_role("admin"))])
async def add_part2_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    add_question("part2", request.question)
    return {"message": "Question added successfully", "question": request.question}

@router.get("/part3")
async def get_part3_questions(current_user: dict = Depends(get_current_user)):
    return {"questions": get_all_questions_by_part("part3")}

@router.post("/part3", dependencies=[Depends(require_role("admin"))])
async def add_part3_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    add_question("part3", request.question)
    return {"message": "Question added successfully", "question": request.question}

@router.get("/all-questions", dependencies=[Depends(require_role("admin"))])
async def list_all_questions():
    return get_all_questions()