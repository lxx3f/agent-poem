from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.poetry import router as poetry_router
from app.api.conversation import router as conversation_router
from app.api.auth import router as auth_router
from app.api.message import router as message_router
from app.api.agent import router as agent_router
from fastapi.exceptions import RequestValidationError

from app.core.exceptions import (
    BusinessException,
    business_exception_handler,
    validation_exception_handler,
)
from app.core.logger import setup_logger
from app.core.middleware import request_id_middleware

setup_logger()

app = FastAPI(title="PoemCloud API")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(request_id_middleware)
app.include_router(poetry_router)
app.include_router(conversation_router)
app.include_router(auth_router)
app.include_router(message_router)
app.include_router(agent_router)

app.add_exception_handler(BusinessException, business_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
