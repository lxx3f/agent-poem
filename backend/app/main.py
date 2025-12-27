from fastapi import FastAPI
from backend.app.api.poetry import router as poetry_router
from fastapi.exceptions import RequestValidationError

from backend.app.core.exceptions import (
    BusinessException,
    business_exception_handler,
    validation_exception_handler,
)

app = FastAPI()
app.include_router(poetry_router)

app.add_exception_handler(BusinessException, business_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
