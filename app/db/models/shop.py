from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base import Base


class ShopOffer(Base):
    __tablename__ = "shop_offers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    catalog_item_id = Column(Integer, ForeignKey("inventory_items_catalog.id"), nullable=False)
    price_gold = Column(Integer, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_limited = Column(Boolean, default=False, nullable=False)

    catalog_item = relationship("InventoryItemCatalog")
