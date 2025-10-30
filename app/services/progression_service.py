from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import List, Optional

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
    rewards: List[dict] = field(default_factory=list)


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
    level_up_rewards: List[dict]


class ProgressionService:
    """Encapsulates XP progression and daily reward logic for players."""

    LEVEL_ENERGY_BONUS = 5
    LEVEL_TITLES = {
        1: "Початківець Шляху",
        2: "Дослідник Вітрів",
        3: "Оберігач Сутінків",
        4: "Голос Ночі",
        5: "Провідник Світла",
    }
    LEVEL_COSMETICS = {
        2: "mask_dusk_epic",
        4: "cloak_traveler_rare",
    }

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
                rewards=[],
            )

        player.xp += amount
        levels_gained = 0
        rewards: List[dict] = []

        while player.xp >= self.xp_required_for_next_level(player.level):
            player.xp -= self.xp_required_for_next_level(player.level)
            player.level += 1
            levels_gained += 1

            energy_before = player.energy
            player.energy = min(player.max_energy, player.energy + self.LEVEL_ENERGY_BONUS)
            energy_bonus = player.energy - energy_before

            rewards.append(
                {
                    "level": player.level,
                    "title": self.LEVEL_TITLES.get(player.level, f"Мандрівник рівня {player.level}"),
                    "energy_bonus": energy_bonus,
                    "cosmetic_unlock": self.LEVEL_COSMETICS.get(player.level),
                }
            )

        self._session.add(player)

        return LevelUpResult(
            xp_gained=amount,
            levels_gained=levels_gained,
            new_level=player.level,
            xp_into_current_level=player.xp,
            xp_needed_for_next_level=self.xp_required_for_next_level(player.level),
            rewards=rewards,
        )

    def can_claim_daily(self, player: Player, now: Optional[datetime] = None) -> bool:
        now = now or datetime.now(timezone.utc)
        if player.last_daily_claim_at is None:
            return True
        last_claim = player.last_daily_claim_at
        if last_claim.tzinfo is None:
            last_claim = last_claim.replace(tzinfo=timezone.utc)
        return now - last_claim >= DAILY_REWARD_COOLDOWN

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
            level_up_rewards=xp_result.rewards,
        )

    @classmethod
    def xp_to_next_level(cls, player: Player) -> int:
        threshold = cls.xp_required_for_next_level(player.level)
        return max(0, threshold - player.xp)

    @classmethod
    def build_milestone(cls, player: Player) -> dict:
        target = 5
        if player.level <= 1:
            current = 0
        else:
            current = (player.level - 1) % target
            if current == 0 and player.level > 1:
                current = target
        return {
            "label": "До титулу 'Голос Ночі'",
            "current": current,
            "target": target,
            "reward_preview": "Епічний Плащ Ночі",
        }
