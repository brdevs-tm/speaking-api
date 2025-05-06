import json
import random
from pathlib import Path

def load_questions():
    questions_path = Path(__file__).parent.parent / "data" / "questions.json"
    with open(questions_path, "r") as f:
        return json.load(f)

def get_random_question(part: str) -> str:
    questions = load_questions()
    return random.choice(questions[part])