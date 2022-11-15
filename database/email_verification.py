from typing import List

from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from pydantic import BaseModel, EmailStr
from router.auth.config import Settings, get_settings

auth_config_settings:Settings = get_settings()

class EmailSchema(BaseModel):
    email: List[EmailStr]


conf = ConnectionConfig(
    MAIL_USERNAME = auth_config_settings.MAIL_USERNAME,
    MAIL_PASSWORD = auth_config_settings.MAIL_PASSWORD,
    MAIL_FROM = auth_config_settings.MAIL_USERNAME,
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_FROM_NAME="Citizen",
    MAIL_TLS = True,
    MAIL_SSL = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

html = """
        <html>
            <body>
                <h1>Hello</h1>
                <p>This is a test email from Fastapi-Mail module</p>
                <a href='http://127.0.0.1:8000/auth/verification/{}/'>
                Click here to verify your email
                </a>
            </body>
        </html>
        """

async def send_verification_email(
    email: EmailStr,
    token: str,
    background_tasks: BackgroundTasks,
    ) :
    message = MessageSchema(
        subject="Verify your email",
        recipients=[email],  # List of recipients, as many as you can pass 
        subtype="html",
        html=html.format(token),
        )

    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message,message)
    return JSONResponse(status_code=200, content={"detail": "email has been sent"})
