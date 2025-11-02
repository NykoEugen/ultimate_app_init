from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class PlantType(Base):
    """Catalog of plants that can be grown on a farm."""

    __tablename__ = "farm_plant_catalog"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    growth_seconds = Column(Integer, nullable=False, default=600)
    xp_reward = Column(Integer, nullable=False, default=15)
    energy_cost = Column(Integer, nullable=False, default=2)
    seed_cost = Column(Integer, nullable=False, default=0)
    sell_price = Column(Integer, nullable=False, default=0)
    unlock_level = Column(Integer, nullable=False, default=1)
    unlock_farming_level = Column(Integer, nullable=False, default=1)
    icon = Column(String, nullable=True)

    crops = relationship("PlantedCrop", back_populates="plant_type")


class PlayerFarmingStats(Base):
    """Aggregated farming progression for a player."""

    __tablename__ = "farm_player_stats"

    player_id = Column(BigInteger, ForeignKey("players.id"), primary_key=True)
    level = Column(Integer, nullable=False, default=1)
    xp = Column(Integer, nullable=False, default=0)
    energy = Column(Integer, nullable=False, default=30)
    max_energy = Column(Integer, nullable=False, default=30)
    tool_level = Column(Integer, nullable=False, default=1)
    tool_name = Column(String, nullable=False, default="Дерев'яна сапка")
    tool_bonus_percent = Column(Integer, nullable=False, default=0)
    last_energy_refill_at = Column(DateTime(timezone=True), nullable=True)
    starter_seed_charges = Column(Integer, nullable=False, default=1)

    player = relationship("Player", back_populates="farming_stats")


class FarmPlot(Base):
    """A single patch of land the player can cultivate."""

    __tablename__ = "farm_plots"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(BigInteger, ForeignKey("players.id"), nullable=False, index=True)
    slot_index = Column(Integer, nullable=False)
    unlocked = Column(Boolean, nullable=False, default=False)
    unlock_cost = Column(Integer, nullable=False, default=200)
    unlock_level_requirement = Column(Integer, nullable=False, default=1)
    unlock_farming_level_requirement = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("Player", back_populates="farm_plots")
    crop = relationship(
        "PlantedCrop",
        uselist=False,
        back_populates="plot",
        cascade="all, delete-orphan",
        single_parent=True,
    )


class PlantedCrop(Base):
    """Represents an in-progress or finished crop on a plot."""

    __tablename__ = "farm_planted_crops"

    id = Column(Integer, primary_key=True, index=True)
    plot_id = Column(Integer, ForeignKey("farm_plots.id"), nullable=False, unique=True)
    plant_type_id = Column(Integer, ForeignKey("farm_plant_catalog.id"), nullable=False)
    planted_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    ready_at = Column(DateTime(timezone=True), nullable=False)
    harvested_at = Column(DateTime(timezone=True), nullable=True)
    state = Column(String, nullable=False, default="growing")  # growing|ready|harvested

    plot = relationship("FarmPlot", back_populates="crop")
    plant_type = relationship("PlantType", back_populates="crops")

    def mark_ready(self, ready_time: datetime) -> None:
        """Set the crop state to ready if growth completed."""
        if self.state != "growing":
            return
        ready_target = self.ready_at
        if ready_target.tzinfo is None:
            ready_target = ready_target.replace(tzinfo=timezone.utc)
        candidate = ready_time
        if candidate.tzinfo is None:
            candidate = candidate.replace(tzinfo=timezone.utc)
        if candidate >= ready_target:
            self.state = "ready"
