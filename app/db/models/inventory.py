from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class InventoryItemCatalog(Base):
    """
    Довідник всіх можливих айтемів у грі.
    """
    __tablename__ = "inventory_items_catalog"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slot = Column(String, nullable=False, default="misc")  # head/chest/cloak/etc
    rarity = Column(String, default="common", nullable=False)  # common/rare/epic/seasonal
    cosmetic = Column(Boolean, default=False, nullable=False) # true = скіни/стиль, false = корисний айтем
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)  # ідентифікатор або url іконки

class InventoryItem(Base):
    """
    Конкретний айтем, що належить гравцю.
    """
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    catalog_item_id = Column(Integer, ForeignKey("inventory_items_catalog.id"), nullable=False)

    is_equipped = Column(Boolean, default=False, nullable=False)

    owner = relationship("Player", back_populates="inventory_items")
    catalog_item = relationship("InventoryItemCatalog")
