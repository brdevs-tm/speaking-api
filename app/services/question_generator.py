import json
import random
from pathlib import Path

def load_questions():
    questions_path = Path(__file__).parent.parent / "data" / "questions.json"
    with open(questions_path, "r") as f:
        return json.load(f)

def save_questions(questions):
    questions_path = Path(__file__).parent.parent / "data" / "questions.json"
    with open(questions_path, "w") as f:
        json.dump(questions, f, indent=4)

def get_random_question(part: str) -> str:
    questions = load_questions()
    return random.choice(questions[part])

def add_question(part: str, question: str):
    questions = load_questions()
    if part not in questions:
        raise ValueError(f"Invalid part: {part}")
    questions[part].append(question)
    save_questions(questions)