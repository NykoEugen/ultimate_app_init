from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.player import Player
from app.utils.exceptions import DailyRewardUnavailable


BASE_XP_THRESHOLD = 100
XP_GROWTH_FACTOR = 1.15
DAILY_REWARD_COOLDOWN = timedelta(hours=24)
DAILY_REWARD_XP = 50
DAILY_REWARD_ENERGY = 5
DAILY_REWARD_GOLD = 100


@dataclass
class LevelUpResult:
    xp_gained: int
    levels_gained: int
    new_level: int
    xp_into_current_level: int
    xp_needed_for_next_level: int


@dataclass
class DailyRewardResult:
    xp_gained: int
    levels_gained: int
    new_level: int
    xp_into_current_level: int
    xp_needed_for_next_level: int
    energy_gained: int
    new_energy: int
    gold_gained: int
    new_gold_total: int
    claimed_at: datetime


class ProgressionService:
    """Encapsulates XP progression and daily reward logic for players."""

    def __init__(self, session: Session):
        self._session = session

    @staticmethod
    def xp_required_for_next_level(level: int) -> int:
        """Return the XP required to level up from the provided level."""
        if level < 1:
            level = 1
        threshold = BASE_XP_THRESHOLD * (XP_GROWTH_FACTOR ** (level - 1))
        return max(1, int(threshold))

    def give_xp(self, player: Player, amount: int) -> LevelUpResult:
        if amount <= 0:
            return LevelUpResult(
                xp_gained=0,
                levels_gained=0,
                new_level=player.level,
                xp_into_current_level=player.xp,
                xp_needed_for_next_level=self.xp_required_for_next_level(player.level),
            )

        player.xp += amount
        levels_gained = 0

        while player.xp >= self.xp_required_for_next_level(player.level):
            player.xp -= self.xp_required_for_next_level(player.level)
            player.level += 1
            levels_gained += 1

        self._session.add(player)

        return LevelUpResult(
            xp_gained=amount,
            levels_gained=levels_gained,
            new_level=player.level,
            xp_into_current_level=player.xp,
            xp_needed_for_next_level=self.xp_required_for_next_level(player.level),
        )

    def can_claim_daily(self, player: Player, now: Optional[datetime] = None) -> bool:
        now = now or datetime.now(timezone.utc)
        if player.last_daily_claim_at is None:
            return True
        return now - player.last_daily_claim_at >= DAILY_REWARD_COOLDOWN

    def claim_daily(self, player: Player, now: Optional[datetime] = None) -> DailyRewardResult:
        now = now or datetime.now(timezone.utc)
        if not self.can_claim_daily(player, now):
            raise DailyRewardUnavailable("Daily reward already claimed in the last 24 hours")

        xp_result = self.give_xp(player, DAILY_REWARD_XP)

        energy_before = player.energy
        player.energy = min(player.max_energy, energy_before + DAILY_REWARD_ENERGY)
        energy_gained = player.energy - energy_before

        current_gold = getattr(player, "gold", 0)
        new_gold_total = current_gold + DAILY_REWARD_GOLD
        setattr(player, "gold", new_gold_total)

        player.last_daily_claim_at = now
        self._session.add(player)

        return DailyRewardResult(
            xp_gained=DAILY_REWARD_XP,
            levels_gained=xp_result.levels_gained,
            new_level=player.level,
            xp_into_current_level=player.xp,
            xp_needed_for_next_level=xp_result.xp_needed_for_next_level,
            energy_gained=energy_gained,
            new_energy=player.energy,
            gold_gained=DAILY_REWARD_GOLD,
            new_gold_total=new_gold_total,
            claimed_at=now,
        )
