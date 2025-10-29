from fastapi import APIRouter

from app.routes.player_routes import router as player_router
from app.routes.quest_routes import router as quest_router


api_router = APIRouter()
api_router.include_router(player_router)
api_router.include_router(quest_router)


__all__ = ["api_router"]
