from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import JSONResponse
from typing import List, Optional

from .colmap.router import router as colmap_router

class ErrorMessage(BaseModel):
    msg: str

class ErrorResponse(BaseModel):
    detail: Optional[List[ErrorMessage]]

api_router = APIRouter(
    prefix="/engine"
)

api_router.include_router(
    colmap_router, prefix="/preprocess/colmap", tags=["colmap"]
)