from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

from .preprocess_video.router import router as preprocess_router

class ErrorMessage(BaseModel):
    msg: str

class ErrorResponse(BaseModel):
    detail: Optional[List[ErrorMessage]]
    
api_router = APIRouter(
    prefix="/nerfstudio"
)

api_router.include_router(
    preprocess_router, tags = ["preprocess"]
)