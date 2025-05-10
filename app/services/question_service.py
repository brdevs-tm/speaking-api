import sqlite3
from pathlib import Path
from datetime import datetime

def init_db():
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop the old questions table if it exists
    cursor.execute("DROP TABLE IF EXISTS questions")

    # Create separate tables for each part with IDs starting from 0
    for part in ["part1", "part2", "part3"]:
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {part}_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL
            )
        ''')

    # Create visits table to track user visits
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            device_id TEXT NOT NULL,
            page TEXT NOT NULL,
            start_time TEXT NOT NULL,
            duration INTEGER NOT NULL  -- Duration in seconds
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

    # Populate each table, resetting IDs to start from 0
    for part, questions in initial_questions.items():
        # Clear existing data
        cursor.execute(f"DELETE FROM {part}_questions")
        # Reset the SQLite sequence to start IDs from 0
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{part}_questions'")
        # Insert questions
        for question in questions:
            cursor.execute(f"INSERT INTO {part}_questions (question) VALUES (?)", (question,))

    conn.commit()
    conn.close()

def track_visit(user_id, device_id, page, duration):
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    start_time = datetime.utcnow().isoformat()
    cursor.execute(
        "INSERT INTO visits (user_id, device_id, page, start_time, duration) VALUES (?, ?, ?, ?, ?)",
        (user_id, device_id, page, start_time, duration)
    )
    conn.commit()
    conn.close()

def get_metrics():
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Total unique users
    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM visits")
    total_users = cursor.fetchone()[0]

    # Total visits
    cursor.execute("SELECT COUNT(*) FROM visits")
    total_visits = cursor.fetchone()[0]

    # Average time spent (in seconds)
    cursor.execute("SELECT AVG(duration) FROM visits")
    avg_time_spent = cursor.fetchone()[0] or 0

    # Recent visits
    cursor.execute("SELECT id, user_id, device_id, page, start_time, duration FROM visits ORDER BY start_time DESC LIMIT 10")
    recent_visits = [
        {"id": row[0], "user_id": row[1], "device_id": row[2], "page": row[3], "timestamp": row[4], "duration": row[5]}
        for row in cursor.fetchall()
    ]

    # Time spent per user
    cursor.execute("SELECT user_id, SUM(duration) as total_duration FROM visits GROUP BY user_id")
    user_durations = [{"user_id": row[0], "total_duration": row[1]} for row in cursor.fetchall()]

    conn.close()
    return {
        "total_users": total_users,
        "total_visits": total_visits,
        "average_time_spent": int(avg_time_spent),
        "recent_visits": recent_visits,
        "user_durations": user_durations
    }

def get_all_questions(part=None):
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if part:
        cursor.execute(f"SELECT id, question FROM {part}_questions")
        questions = [{"id": row[0], "question": row[1]} for row in cursor.fetchall()]
    else:
        questions = []
        for p in ["part1", "part2", "part3"]:
            cursor.execute(f"SELECT id, question FROM {p}_questions")
            part_questions = [{"id": row[0], "part": p, "question": row[1]} for row in cursor.fetchall()]
            questions.extend(part_questions)

    conn.close()
    return questions

def get_question_by_id(part, question_id):
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT question FROM {part}_questions WHERE id = ?", (question_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "Unknown Question"

def add_question(part, question):
    if part not in ["part1", "part2", "part3"]:
        raise ValueError(f"Invalid part: {part}")
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO {part}_questions (question) VALUES (?)", (question,))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def delete_question(part, question_id):
    if part not in ["part1", "part2", "part3"]:
        raise ValueError(f"Invalid part: {part}")
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM {part}_questions WHERE id = ?", (question_id,))
    if cursor.fetchone() is None:
        conn.close()
        return False
    cursor.execute(f"DELETE FROM {part}_questions WHERE id = ?", (question_id,))
    # Re-sequence IDs to maintain continuity
    cursor.execute(f"SELECT id, question FROM {part}_questions ORDER BY id")
    remaining = cursor.fetchall()
    cursor.execute(f"DELETE FROM {part}_questions")
    cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{part}_questions'")
    for idx, (_, question) in enumerate(remaining):
        cursor.execute(f"INSERT INTO {part}_questions (id, question) VALUES (?, ?)", (idx, question))
    conn.commit()
    conn.close()
    return True

def update_question(part, question_id, new_question):
    if part not in ["part1", "part2", "part3"]:
        raise ValueError(f"Invalid part: {part}")
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM {part}_questions WHERE id = ?", (question_id,))
    if cursor.fetchone() is None:
        conn.close()
        return False
    cursor.execute(f"UPDATE {part}_questions SET question = ? WHERE id = ?", (new_question, question_id))
    conn.commit()
    conn.close()
    return True

def search_questions(query):
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    results = []
    for part in ["part1", "part2", "part3"]:
        cursor.execute(f"SELECT id, question FROM {part}_questions WHERE question LIKE ?", ('%' + query + '%',))
        part_results = [{"id": row[0], "part": part, "question": row[1]} for row in cursor.fetchall()]
        results.extend(part_results)
    conn.close()
    return results

def get_question_count():
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    counts = {}
    for part in ["part1", "part2", "part3"]:
        cursor.execute(f"SELECT COUNT(*) FROM {part}_questions")
        counts[part] = cursor.fetchone()[0]
    conn.close()
    return counts

def import_questions(questions_data):
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    success_count = 0
    for item in questions_data:
        part = item.get("part")
        question = item.get("question")
        if part in ["part1", "part2", "part3"] and question and question.strip():
            cursor.execute(f"INSERT INTO {part}_questions (question) VALUES (?)", (question,))
            success_count += 1
    # Re-sequence IDs after import
    for part in ["part1", "part2", "part3"]:
        cursor.execute(f"SELECT id, question FROM {part}_questions ORDER BY id")
        questions = cursor.fetchall()
        cursor.execute(f"DELETE FROM {part}_questions")
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{part}_questions'")
        for idx, (_, question) in enumerate(questions):
            cursor.execute(f"INSERT INTO {part}_questions (id, question) VALUES (?, ?)", (idx, question))
    conn.commit()
    conn.close()
    return success_count

init_db()