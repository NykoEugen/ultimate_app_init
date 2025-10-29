from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

class Player(Base):
    __tablename__ = "players"

    id = Column(BigInteger, primary_key=True, index=True)  
    # Ми можемо прямо використовувати telegram_user_id як id, щоб не мучитись з мапінгом

    username = Column(String, nullable=True)  # видно в рейтингах

    level = Column(Integer, default=1, nullable=False)
    xp = Column(Integer, default=0, nullable=False)

    energy = Column(Integer, default=20, nullable=False)     # витрачається на дії
    max_energy = Column(Integer, default=20, nullable=False)

    gold = Column(Integer, default=0, nullable=False)

    last_daily_claim_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    inventory_items = relationship("InventoryItem", back_populates="owner")
    quest_progress = relationship("QuestProgress", back_populates="player", uselist=False)
