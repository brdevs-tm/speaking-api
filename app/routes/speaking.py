from fastapi import APIRouter, Depends, HTTPException
from app.services.question_service import (
    get_all_questions,
    add_question,
    delete_question,
    update_question,
    search_questions,
    get_question_count,
    import_questions,
    get_question_by_id,
    track_visit,
    get_metrics
)
from app.models.schemas import QuestionRequest, QuestionUpdate, QuestionSearch, BatchImport
from app.dependencies.auth import get_current_user, require_role
from app.services.telegram_bot import send_telegram_notification

router = APIRouter(prefix="/api/speaking", tags=["speaking"])

@router.get("/part1")
async def get_part1_questions(user_id: str = "anonymous", device_id: str = "unknown"):
    questions = get_all_questions("part1")
    # Track the visit
    track_visit(user_id, device_id, "Part 1", 120)  # Assume 120 seconds for now
    return {"questions": [q["question"] for q in questions]}

@router.post("/part1", dependencies=[Depends(require_role("admin"))])
async def add_part1_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    new_id = add_question("part1", request.question)
    message = f"New Question Added to Part 1:\nID: {new_id}\nQuestion: {request.question}"
    await send_telegram_notification(message)
    return {"message": "Question added successfully", "question": request.question}

@router.get("/part2")
async def get_part2_questions(user_id: str = "anonymous", device_id: str = "unknown"):
    questions = get_all_questions("part2")
    # Track the visit
    track_visit(user_id, device_id, "Part 2", 150)  # Assume 150 seconds for now
    return {"questions": [q["question"] for q in questions]}

@router.post("/part2", dependencies=[Depends(require_role("admin"))])
async def add_part2_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    new_id = add_question("part2", request.question)
    message = f"New Question Added to Part 2:\nID: {new_id}\nQuestion: {request.question}"
    await send_telegram_notification(message)
    return {"message": "Question added successfully", "question": request.question}

@router.get("/part3")
async def get_part3_questions(user_id: str = "anonymous", device_id: str = "unknown"):
    questions = get_all_questions("part3")
    # Track the visit
    track_visit(user_id, device_id, "Part 3", 180)  # Assume 180 seconds for now
    return {"questions": [q["question"] for q in questions]}

@router.post("/part3", dependencies=[Depends(require_role("admin"))])
async def add_part3_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    new_id = add_question("part3", request.question)
    message = f"New Question Added to Part 3:\nID: {new_id}\nQuestion: {request.question}"
    await send_telegram_notification(message)
    return {"message": "Question added successfully", "question": request.question}

@router.get("/all-questions", dependencies=[Depends(require_role("admin"))])
async def list_all_questions():
    return get_all_questions()

@router.delete("/{part}/{question_id}", dependencies=[Depends(require_role("admin"))])
async def delete_part_question(part: str, question_id: int):
    old_question = get_question_by_id(part, question_id)
    success = delete_question(part, question_id)
    if success:
        message = f"Question Deleted from {part}:\nID: {question_id}\nQuestion: {old_question}"
        await send_telegram_notification(message)
        return {"message": f"Question {question_id} deleted from {part}"}
    raise HTTPException(status_code=404, detail="Question not found")

@router.put("/{part}/{question_id}", dependencies=[Depends(require_role("admin"))])
async def update_part_question(part: str, question_id: int, request: QuestionUpdate):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    old_question = get_question_by_id(part, question_id)
    success = update_question(part, question_id, request.question)
    if success:
        message = (
            f"Question Updated in {part}:\n"
            f"ID: {question_id}\n"
            f"Old Question: {old_question}\n"
            f"New Question: {request.question}"
        )
        await send_telegram_notification(message)
        return {"message": f"Question {question_id} updated in {part}"}
    raise HTTPException(status_code=404, detail="Question not found")

@router.get("/search", dependencies=[Depends(require_role("admin"))])
async def search_questions_endpoint(search: QuestionSearch):
    results = search_questions(search.query)
    return {"results": results}

@router.get("/count", dependencies=[Depends(require_role("admin"))])
async def get_counts():
    return get_question_count()

@router.post("/import", dependencies=[Depends(require_role("admin"))])
async def import_batch_questions(import_data: BatchImport):
    success_count = import_questions(import_data.questions)
    message = (
        "Batch Import Completed:\n"
        f"Imported {success_count} questions:\n"
        "\n".join([f"Part: {q['part']}, Question: {q['question']}" for q in import_data.questions])
    )
    await send_telegram_notification(message)
    return {"message": f"Imported {success_count} questions successfully"}

@router.get("/metrics", dependencies=[Depends(require_role("admin"))])
async def get_admin_metrics():
    return get_metrics()