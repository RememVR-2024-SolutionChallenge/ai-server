from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

from .preprocess.router import router as preprocess_router
from .train_avatar.router import router as train_avatar_router
from .train_scene.router import router as train_scene_router


class ErrorMessage(BaseModel):
    msg: str

class ErrorResponse(BaseModel):
    detail: Optional[List[ErrorMessage]]
    
api_router = APIRouter(
    prefix="/engine"
)

api_router.include_router(
    preprocess_router, prefix="nerfstudio", tags = ["preprocess"]
)

api_router.include_router(
    train_avatar_router, prefix="nerfstudio", tags = ["avatar"]
)

api_router.include_router(
    train_scene_router, prefix="nerfstudio", tags = ["scene"]
)
