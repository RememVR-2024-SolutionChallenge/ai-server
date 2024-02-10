from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

from .train_avatar.router import router as avatar_router
from .train_scene.router import router as scene_router

class ErrorMessage(BaseModel):
    msg: str

class ErrorResponse(BaseModel):
    detail: Optional[List[ErrorMessage]]
    
api_router = APIRouter(
    prefix="/train"
)

api_router.include_router(
    avatar_router, tags = ["avatar"]
)

api_router.include_router(
    scene_router, tags = ["scene"]
)