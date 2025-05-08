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

def get_all_questions(part=None):
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if part:
        cursor.execute("SELECT question FROM questions WHERE part = ?", (part,))
        questions = [row[0] for row in cursor.fetchall()]
    else:
        cursor.execute("SELECT id, part, question FROM questions")  # Include ID for management
        questions = [{"id": row[0], "part": row[1], "question": row[2]} for row in cursor.fetchall()]
    conn.close()
    return questions

def get_question_by_id(part, question_id):
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT question FROM questions WHERE id = ? AND part = ?", (question_id, part))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "Unknown Question"

def add_question(part, question):
    if part not in ["part1", "part2", "part3"]:
        raise ValueError(f"Invalid part: {part}")
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO questions (part, question) VALUES (?, ?)", (part, question))
    conn.commit()
    conn.close()

def delete_question(part, question_id):
    if part not in ["part1", "part2", "part3"]:
        raise ValueError(f"Invalid part: {part}")
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM questions WHERE id = ? AND part = ?", (question_id, part))
    if cursor.fetchone() is None:
        conn.close()
        return False
    cursor.execute("DELETE FROM questions WHERE id = ? AND part = ?", (question_id, part))
    conn.commit()
    conn.close()
    return True

def update_question(part, question_id, new_question):
    if part not in ["part1", "part2", "part3"]:
        raise ValueError(f"Invalid part: {part}")
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM questions WHERE id = ? AND part = ?", (question_id, part))
    if cursor.fetchone() is None:
        conn.close()
        return False
    cursor.execute("UPDATE questions SET question = ? WHERE id = ? AND part = ?", (new_question, question_id, part))
    conn.commit()
    conn.close()
    return True

def search_questions(query):
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, part, question FROM questions WHERE question LIKE ?", ('%' + query + '%',))
    results = [{"id": row[0], "part": row[1], "question": row[2]} for row in cursor.fetchall()]
    conn.close()
    return results

def get_question_count():
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT part, COUNT(*) as count FROM questions GROUP BY part")
    counts = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return {
        "part1": counts.get("part1", 0),
        "part2": counts.get("part2", 0),
        "part3": counts.get("part3", 0)
    }

def import_questions(questions_data):
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    success_count = 0
    for item in questions_data:
        part = item.get("part")
        question = item.get("question")
        if part in ["part1", "part2", "part3"] and question and question.strip():
            cursor.execute("INSERT INTO questions (part, question) VALUES (?, ?)", (part, question))
            success_count += 1
    conn.commit()
    conn.close()
    return success_count

init_db()