from __future__ import annotations

from pydantic import BaseModel


class ShopPurchaseRequest(BaseModel):
    offer_id: int
