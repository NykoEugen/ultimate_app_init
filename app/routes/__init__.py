from fastapi import APIRouter

from app.routes.dashboard_routes import router as dashboard_router
from app.routes.inventory_routes import router as inventory_router
from app.routes.meta_routes import router as meta_router
from app.routes.player_routes import router as player_router
from app.routes.progression_routes import router as progression_router
from app.routes.shop_routes import router as shop_router
from app.routes.quest_routes import router as quest_router
from app.routes.reward_routes import router as reward_router
from app.routes.farm_routes import router as farm_router
from app.routes.onboarding_routes import router as onboarding_router
from app.routes.admin_routes import router as admin_router


api_router = APIRouter()
api_router.include_router(meta_router)
api_router.include_router(player_router)
api_router.include_router(quest_router)
api_router.include_router(dashboard_router)
api_router.include_router(reward_router)
api_router.include_router(inventory_router)
api_router.include_router(progression_router)
api_router.include_router(shop_router)
api_router.include_router(farm_router)
api_router.include_router(onboarding_router)
api_router.include_router(admin_router)


__all__ = ["api_router"]
