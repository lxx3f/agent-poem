from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.response import StandardResponse


class BusinessException(Exception):

    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message


def business_exception_handler(_: Request, exc: Exception):
    assert isinstance(exc, BusinessException)
    return JSONResponse(
        status_code=200,
        content=StandardResponse(
            code=exc.code,
            message=exc.message,
            data=None,
        ).model_dump(),
    )


def validation_exception_handler(_: Request, exc: Exception):
    assert isinstance(exc, RequestValidationError)
    return JSONResponse(
        status_code=422,
        content=StandardResponse(
            code=422,
            message=str(exc),
            data=None,
        ).model_dump(),
    )
