from fastapi import FastAPI
from .questions.question import question_router
from .options.option import option_router
from .auth.auth import auth_router
from .auth.email import email_router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8001",
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(question_router)
app.include_router(option_router)
app.include_router(email_router)

@app.get('/')
def hello():
    return "hello"     