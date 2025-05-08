import sqlite3
import os
from pathlib import Path
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException

SECRET_KEY = os.getenv("SECRET_KEY", "acd8b91069b37d030a777c85c2f9c4ef")  # Productionda .env'dan oling
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Drop existing users table to avoid schema mismatch
    cursor.execute("DROP TABLE IF EXISTS users")
    # Create users table with correct schema
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    ''')
    # Dastlabki adminni qo'shish
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'iynemlive'")
    if cursor.fetchone()[0] == 0:
        hashed_password = pwd_context.hash("jahongir_04")
        cursor.execute(
            "INSERT INTO users (username, password, name, role) VALUES (?, ?, ?, ?)",
            ("iynemlive", hashed_password, "Jahongir", "admin")
        )
    conn.commit()
    conn.close()

def authenticate_user(username: str, password: str):
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password, role FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if not user or not pwd_context.verify(password, user[2]):
        return None
    access_token = create_access_token({"sub": str(user[0]), "role": user[3], "username": user[1]})
    return {"id": user[0], "username": user[1], "role": user[3], "token": access_token}

def update_admin_credentials(new_username: str, new_password: str):
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    hashed_password = pwd_context.hash(new_password)
    try:
        cursor.execute(
            "UPDATE users SET username = ?, password = ? WHERE username = 'iynemlive'",
            (new_username, hashed_password)
        )
        if cursor.rowcount == 0:
            return False
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        conn.rollback()
        return False
    finally:
        conn.close()

def get_current_admin_credentials():
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM users WHERE username = 'iynemlive'")
    user = cursor.fetchone()
    conn.close()
    if user:
        return {"username": user[0], "password": user[1]}
    return {"username": "Unknown", "password": "Unknown"}

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

init_db()