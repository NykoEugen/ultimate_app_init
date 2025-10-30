from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base import Base


class Wallet(Base):
    __tablename__ = "wallets"

    player_id = Column(Integer, ForeignKey("players.id"), primary_key=True)
    gold = Column(Integer, default=0, nullable=False)

    player = relationship("Player", back_populates="wallet")
