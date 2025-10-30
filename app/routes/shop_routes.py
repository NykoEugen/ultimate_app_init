from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.shop import ShopPurchaseRequest
from app.services.shop_service import buy_offer, list_shop_offers
from app.utils.exceptions import InsufficientFunds, ShopOfferUnavailable


router = APIRouter(prefix="/player/{player_id}/shop", tags=["shop"])


@router.get("")
async def list_shop(player_id: int, db: AsyncSession = Depends(get_db)) -> dict:
    wallet, offers = await list_shop_offers(db, player_id)
    return {
        "wallet": {
            "gold": wallet.gold,
            "gems": 0,
        },
        "offers": offers,
    }


@router.post("/buy")
async def buy_shop_offer(
    player_id: int,
    payload: ShopPurchaseRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        wallet, granted = await buy_offer(db, player_id, payload.offer_id)
    except InsufficientFunds as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ShopOfferUnavailable as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    await db.commit()

    return {
        "status": "purchased",
        "wallet": {
            "gold": wallet.gold,
            "gems": 0,
        },
        "granted": granted,
    }
