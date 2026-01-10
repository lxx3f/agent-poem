from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List

from app.schemas.poetry import PoetrySearchRequest, PoetrySearchResponse, PoetrySearchItem
from app.services.poetry_service import PoetryService
from app.core.response import StandardResponse, success_response, error_response

router = APIRouter(prefix="/api/poetry", tags=["Poetry"])


@router.post("/search", response_model=StandardResponse[PoetrySearchResponse])
def search_poetry(req: PoetrySearchRequest):
    '''
    搜索诗词
    
    :param req: 请求体
    :type req: PoetrySearchRequest
    '''
    poetry_service = PoetryService()
    results = poetry_service.search(
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
    response = PoetrySearchResponse(total=len(items), items=items)
    return success_response(data=response)
