from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List

from backend.app.schemas.poetry import PoetrySearchRequest, PoetrySearchResponse, PoetrySearchItem
from backend.app.services.poetry_service import PoetryService
from backend.app.core.response import StandardResponse, success_response, error_response

router = APIRouter(prefix="/api/poetry", tags=["Poetry"])


@router.post("/search", response_model=StandardResponse[PoetrySearchResponse])
def search_poetry(req: PoetrySearchRequest):
    service = PoetryService()
    results = service.search(
        query=req.query,
        search_type=req.search_type,
        top_k=req.top_k,
    )
    items: List[PoetrySearchItem] = []
    for item in results:
        items.append(
            PoetrySearchItem(
                id=item["id"],
                title=item["title"],
                dynasty=item["dynasty"],
                writer=item["writer"],
                content=item["content"],
                score=item.get("score", None),
            ))

    return success_response(PoetrySearchResponse(total=len(items),
                                                 items=items))
