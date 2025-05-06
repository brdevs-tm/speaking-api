import sqlite3
from pathlib import Path
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.models.schemas import UserCreate

SECRET_KEY = "your-secret-key"  # Productionda .env faylida saqlang
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    ''')
    conn.commit()
    conn.close()

def create_user(user: UserCreate):
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    hashed_password = pwd_context.hash(user.password)
    role = "admin" if user.email == "admin@example.com" else "user"  # Birinchi admin
    try:
        cursor.execute(
            "INSERT INTO users (email, password, name, role) VALUES (?, ?, ?, ?)",
            (user.email, hashed_password, user.name, role)
        )
        user_id = cursor.lastrowid
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError("Email already exists")
    finally:
        conn.close()

def authenticate_user(email: str, password: str):
    db_path = Path(__file__).parent.parent / "data" / "questions.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, password, role FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    if not user or not pwd_context.verify(password, user[2]):
        return None
    access_token = create_access_token({"sub": str(user[0]), "role": user[3]})
    return {"id": user[0], "email": user[1], "role": user[3], "token": access_token}

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

init_db()