from fastapi import FastAPI
from backend.app.api.poetry import router as poetry_router
from backend.app.api.conversation import router as conversation_router
from backend.app.api.auth import router as auth_router
from backend.app.api.chat import router as chat_router
from fastapi.exceptions import RequestValidationError

from backend.app.core.exceptions import (
    BusinessException,
    business_exception_handler,
    validation_exception_handler,
)

app = FastAPI(title="PoemCloud API")
app.include_router(poetry_router)
app.include_router(conversation_router)
app.include_router(auth_router)
app.include_router(chat_router)

app.add_exception_handler(BusinessException, business_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
