from fastapi import APIRouter
from app.services.question_generator import get_random_question

router = APIRouter(prefix="/api/speaking", tags=["speaking"])

@router.get("/part1")
async def get_part1_question():
    return {"question": get_random_question("part1")}

@router.get("/part2")
async def get_part2_question():
    return {"question": get_random_question("part2")}

@router.get("/part3")
async def get_part3_question():
    return {"question": get_random_question("part3")}