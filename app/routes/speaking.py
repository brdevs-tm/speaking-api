from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.question_generator import get_random_question, add_question

router = APIRouter(prefix="/api/speaking", tags=["speaking"])

# Model for POST request body
class QuestionRequest(BaseModel):
    question: str

@router.get("/part1")
async def get_part1_question():
    return {"question": get_random_question("part1")}

@router.post("/part1")
async def add_part1_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    add_question("part1", request.question)
    return {"message": "Question added successfully", "question": request.question}

@router.get("/part2")
async def get_part2_question():
    return {"question": get_random_question("part2")}

@router.post("/part2")
async def add_part2_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    add_question("part2", request.question)
    return {"message": "Question added successfully", "question": request.question}

@router.get("/part3")
async def get_part3_question():
    return {"question": get_random_question("part3")}

@router.post("/part3")
async def add_part3_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    add_question("part3", request.question)
    return {"message": "Question added successfully", "question": request.question}