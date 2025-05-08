import sqlite3
from pathlib import Path

def init_db():
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part TEXT NOT NULL,
            question TEXT NOT NULL
        )
    ''')
    # Initial questions
    initial_questions = {
        "part1": [
            "What is your favorite hobby and why?",
            "Where are you from, and what is it like?",
            "Do you prefer to study alone or with others?",
            "What kind of music do you enjoy listening to?",
            "How do you usually spend your weekends?"
        ],
        "part2": [
            "Describe a memorable holiday you have had.",
            "Talk about a book you have read recently.",
            "Describe a person who has influenced you.",
            "Talk about a place you would like to visit.",
            "Describe a time when you helped someone."
        ],
        "part3": [
            "What are the benefits of international travel?",
            "How does technology affect the way people communicate?",
            "What are the advantages and disadvantages of living in a big city?",
            "How can governments encourage people to live more sustainably?",
            "Why is it important to preserve cultural heritage?"
        ]
    }
    for part, questions in initial_questions.items():
        for question in questions:
            cursor.execute("INSERT OR IGNORE INTO questions (part, question) VALUES (?, ?)", (part, question))
    conn.commit()
    conn.close()

def get_all_questions(part: str = None):
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if part:
        cursor.execute("SELECT question FROM questions WHERE part = ?", (part,))
        questions = [row[0] for row in cursor.fetchall()]
    else:
        cursor.execute("SELECT part, question FROM questions")
        questions = [{"part": row[0], "question": row[1]} for row in cursor.fetchall()]
    conn.close()
    return questions

def save_question(part: str, question: str):
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO questions (part, question) VALUES (?, ?)", (part, question))
    conn.commit()
    conn.close()

def add_question(part: str, question: str):
    if part not in ["part1", "part2", "part3"]:
        raise ValueError(f"Invalid part: {part}")
    save_question(part, question)

init_db()