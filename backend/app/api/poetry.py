from fastapi import APIRouter, Depends, Query, HTTPException

from backend.app.schemas.poetry import PoetrySearchRequest, PoetrySearchResponse
from backend.app.services.poetry_service import PoetryService
from backend.app.core.response import StandardResponse, success_response, error_response

router = APIRouter(prefix="/api/poetry", tags=["Poetry"])


@router.post("/search", response_model=StandardResponse[PoetrySearchResponse])
def search_poetry(req: PoetrySearchRequest):
    service = PoetryService()
    items = service.search(
        query=req.query,
        search_type=req.search_type,
        top_k=req.top_k,
    )
    return success_response(PoetrySearchResponse(total=len(items),
                                                 items=items))
