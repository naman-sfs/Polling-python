import os
from fastapi import BackgroundTasks, APIRouter
from dotenv import load_dotenv
from starlette.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel
from typing import List
load_dotenv('.env')

email_router = APIRouter(prefix="/api/email")

conf = ConnectionConfig(
    MAIL_USERNAME="fastapiemail24@gmail.com",
    MAIL_PASSWORD="qwaszx@12",
    MAIL_FROM="fastapiemail24@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM_NAME="",
    USE_CREDENTIALS=True,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False
)

class EmailSchema(BaseModel):
    email: List[EmailStr]

@email_router.get('/')
def email():
    return "email route"

@email_router.post("/send")
async def send_in_background(
    background_tasks: BackgroundTasks,
    email: EmailSchema
    ) -> JSONResponse:

    message = MessageSchema(
        subject="LogIn",
        recipients=email.dict().get("email"),
        body="LogIn Successful",
        subtype=MessageType.plain)

    fm = FastMail(conf)

    background_tasks.add_task(fm.send_message,message)

    return JSONResponse(status_code=200, content={"message": "email has been sent"})


def send_login_email():
    print("email sent")