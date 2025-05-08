from pydantic import BaseModel

class AdminLogin(BaseModel):
    username: str
    password: str

class AdminUpdate(BaseModel):
    username: str
    password: str

class QuestionRequest(BaseModel):
    question: str