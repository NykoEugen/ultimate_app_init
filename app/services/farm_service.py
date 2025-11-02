from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.models.farm import FarmPlot, PlantType, PlantedCrop, PlayerFarmingStats
from app.db.models.player import Player
from app.db.models.wallet import Wallet
from app.utils.exceptions import (
    FarmPlantLocked,
    FarmPlotEmpty,
    FarmPlotLocked,
    FarmPlotOccupied,
    FarmingToolUpgradeUnavailable,
    InsufficientFunds,
    NotEnoughFarmEnergy,
)


DEFAULT_PLANTS: Tuple[Dict[str, object], ...] = (
    {
        "name": "Соковита морква",
        "description": "Невибаглива культура для перших врожаїв.",
        "growth_seconds": 900,
        "xp_reward": 25,
        "energy_cost": 2,
        "seed_cost": 0,
        "sell_price": 35,
        "unlock_level": 1,
        "unlock_farming_level": 1,
        "icon": "plant_carrot_common",
    },
    {
        "name": "Вербена зоряного сяйва",
        "description": "Легендарна трава, що краще росте поруч із реальними овочами.",
        "growth_seconds": 1500,
        "xp_reward": 40,
        "energy_cost": 3,
        "seed_cost": 55,
        "sell_price": 110,
        "unlock_level": 2,
        "unlock_farming_level": 2,
        "icon": "plant_starverbena_uncommon",
    },
    {
        "name": "Медова полуниця",
        "description": "Швидко росте та додає вітамінів.",
        "growth_seconds": 1800,
        "xp_reward": 45,
        "energy_cost": 3,
        "seed_cost": 40,
        "sell_price": 95,
        "unlock_level": 3,
        "unlock_farming_level": 2,
        "icon": "plant_strawberry_rare",
    },
    {
        "name": "Сонячний гарбуз-глорія",
        "description": "Гібрид гарбуза і фантазійного світляка, світиться уночі.",
        "growth_seconds": 2700,
        "xp_reward": 70,
        "energy_cost": 4,
        "seed_cost": 85,
        "sell_price": 190,
        "unlock_level": 4,
        "unlock_farming_level": 3,
        "icon": "plant_pumpkin_gloria",
    },
    {
        "name": "Місячна лаванда",
        "description": "Рослина для досвідчених фермерів. Дає багато досвіду.",
        "growth_seconds": 3600,
        "xp_reward": 110,
        "energy_cost": 4,
        "seed_cost": 120,
        "sell_price": 260,
        "unlock_level": 6,
        "unlock_farming_level": 4,
        "icon": "plant_lavender_epic",
    },
)

TOOL_UPGRADES: Tuple[Dict[str, object], ...] = (
    {
        "level": 1,
        "name": "Дерев'яна сапка",
        "bonus_percent": 0,
        "cost": 0,
        "required_farming_level": 1,
    },
    {
        "level": 2,
        "name": "Бронзова сапка",
        "bonus_percent": 10,
        "cost": 250,
        "required_farming_level": 2,
    },
    {
        "level": 3,
        "name": "Срібна сапка",
        "bonus_percent": 20,
        "cost": 600,
        "required_farming_level": 4,
    },
    {
        "level": 4,
        "name": "Кришталевий культиватор",
        "bonus_percent": 35,
        "cost": 1200,
        "required_farming_level": 6,
    },
)

BASE_PLOTS = 3
TOTAL_PLOTS = 8
BASE_PLOT_UNLOCK_COST = 400
FARM_XP_BASE_THRESHOLD = 80
FARM_XP_GROWTH_FACTOR = 1.22
FARM_ENERGY_GOLD_PER_POINT = 25
FARM_ENERGY_MAX_CAP = 60
FARM_ENERGY_REGEN_SECONDS = 600  # пасивна регенерація: 1 енергія кожні 10 хвилин


@dataclass
class FarmStateData:
    player: Player
    stats: PlayerFarmingStats
    plots: List[FarmPlot]
    plants: List[PlantType]
    wallet: Wallet
    now: datetime


class FarmService:
    """Domain logic around farming gameplay."""

    def __init__(self, session: Session):
        self._session = session

    def get_farm_state(self, player_id: int, now: Optional[datetime] = None) -> FarmStateData:
        player = self._load_player(player_id)
        now = now or datetime.now(timezone.utc)
        stats = self._ensure_stats(player)
        self._apply_passive_energy_regen(stats, now)
        wallet = self._ensure_wallet(player)
        plants = self._ensure_default_plants()
        plots = self._ensure_plots(player)
        self._update_crop_states(plots, now)
        return FarmStateData(player=player, stats=stats, plots=plots, plants=plants, wallet=wallet, now=now)

    def plant_crop(
        self,
        player_id: int,
        plot_id: int,
        plant_type_id: int,
        now: Optional[datetime] = None,
    ) -> Tuple[FarmStateData, str]:
        now = now or datetime.now(timezone.utc)
        state = self.get_farm_state(player_id, now)
        plot = self._plot_by_id(state.plots, plot_id)
        if not plot.unlocked:
            raise FarmPlotLocked("This plot is still locked")
        if plot.crop is not None:
            raise FarmPlotOccupied("Plot already has a crop")

        plant_type = self._plant_by_id(state.plants, plant_type_id)
        self._guard_plant_requirements(state.player, state.stats, plant_type)
        self._spend_energy(state.stats, plant_type.energy_cost, now)

        wallet = state.wallet
        used_starter_seed = False
        if plant_type.seed_cost > 0:
            if wallet.gold < plant_type.seed_cost:
                if state.stats.starter_seed_charges > 0:
                    state.stats.starter_seed_charges -= 1
                    used_starter_seed = True
                    self._session.add(state.stats)
                else:
                    raise InsufficientFunds(wallet.gold, plant_type.seed_cost)
            else:
                wallet.gold -= plant_type.seed_cost
                state.player.gold = wallet.gold
        else:
            # keep free seeds for more expensive crops but ensure initial charge exists
            if state.stats.starter_seed_charges > 0:
                used_starter_seed = False

        modified_seconds = self._apply_tool_bonus(
            base_seconds=plant_type.growth_seconds,
            bonus_percent=state.stats.tool_bonus_percent,
        )
        ready_at = now + timedelta(seconds=modified_seconds)

        crop = PlantedCrop(plot=plot, plant_type=plant_type, planted_at=now, ready_at=ready_at, state="growing")
        self._session.add(crop)
        self._session.flush()

        message = f"Ви посадили {plant_type.name}. Врожай буде готовий приблизно о {ready_at:%H:%M}."
        if used_starter_seed:
            message += " Використано подарункове насіння."
        refreshed = self.get_farm_state(player_id, now)
        return refreshed, message

    def harvest_crop(
        self,
        player_id: int,
        plot_id: int,
        now: Optional[datetime] = None,
    ) -> Tuple[FarmStateData, str]:
        now = now or datetime.now(timezone.utc)
        state = self.get_farm_state(player_id, now)
        plot = self._plot_by_id(state.plots, plot_id)
        if plot.crop is None:
            raise FarmPlotEmpty("Ділянка порожня.")

        crop = plot.crop
        crop.mark_ready(now)
        if crop.state != "ready":
            remaining = int((crop.ready_at - now).total_seconds())
            remaining = max(remaining, 0)
            raise FarmPlotOccupied(f"Врожай ще росте. Залишилось приблизно {remaining // 60} хв.")

        plant = crop.plant_type
        xp_gain, levels_gained = self._grant_farming_xp(state.stats, plant.xp_reward)

        wallet = state.wallet
        wallet.gold += plant.sell_price
        state.player.gold = wallet.gold

        self._session.delete(crop)
        plot.crop = None
        self._session.flush()

        message_parts = [
            f"Ви зібрали {plant.name} і заробили {plant.sell_price} золотих.",
            f"Отримано {xp_gain} досвіду фермерства.",
        ]
        if levels_gained:
            message_parts.append(f"Рівень ферми підвищено до {state.stats.level}!")
        message = " ".join(message_parts)
        refreshed = self.get_farm_state(player_id, now)
        return refreshed, message

    def unlock_plot(self, player_id: int, plot_id: int) -> Tuple[FarmStateData, str]:
        state = self.get_farm_state(player_id)
        plot = self._plot_by_id(state.plots, plot_id)
        if plot.unlocked:
            return state, "Ділянка вже відкрита."

        if state.player.level < plot.unlock_level_requirement:
            raise FarmPlotLocked("Потрібно підвищити основний рівень персонажа.")
        if state.stats.level < plot.unlock_farming_level_requirement:
            raise FarmPlotLocked("Потрібно підвищити рівень фермерства.")

        wallet = state.wallet
        if wallet.gold < plot.unlock_cost:
            raise InsufficientFunds(wallet.gold, plot.unlock_cost)

        wallet.gold -= plot.unlock_cost
        state.player.gold = wallet.gold
        plot.unlocked = True
        self._session.add(plot)
        self._session.flush()

        message = "Нова ділянка готова до посадки!"
        refreshed = self.get_farm_state(player_id)
        return refreshed, message

    def refill_energy(self, player_id: int, amount: int) -> Tuple[FarmStateData, str]:
        if amount <= 0:
            state = self.get_farm_state(player_id)
            return state, "Нічого не зроблено."

        state = self.get_farm_state(player_id)
        stats = state.stats
        amount = min(amount, stats.max_energy - stats.energy)
        if amount <= 0:
            return state, "Енергія вже повна."

        gold_required = amount * FARM_ENERGY_GOLD_PER_POINT

        wallet = state.wallet
        if wallet.gold < gold_required:
            raise InsufficientFunds(wallet.gold, gold_required)

        wallet.gold -= gold_required
        state.player.gold = wallet.gold
        stats.energy += amount
        stats.energy = min(stats.energy, stats.max_energy)
        stats.last_energy_refill_at = datetime.now(timezone.utc)
        self._session.add(stats)
        self._session.flush()

        message = f"Поповнено {amount} енергії ферми."
        refreshed = self.get_farm_state(player_id)
        return refreshed, message

    def upgrade_tool(self, player_id: int) -> Tuple[FarmStateData, str]:
        state = self.get_farm_state(player_id)
        current_tool_level = state.stats.tool_level
        next_tool = self._find_tool_upgrade(current_tool_level + 1)
        if next_tool is None:
            raise FarmingToolUpgradeUnavailable("Інструмент вже максимального рівня.")
        if state.stats.level < next_tool["required_farming_level"]:
            raise FarmingToolUpgradeUnavailable("Замало рівня фермерства для покращення інструмента.")

        wallet = state.wallet
        cost = int(next_tool["cost"])
        if wallet.gold < cost:
            raise InsufficientFunds(wallet.gold, cost)

        wallet.gold -= cost
        state.player.gold = wallet.gold
        state.stats.tool_level = next_tool["level"]
        state.stats.tool_name = next_tool["name"]
        state.stats.tool_bonus_percent = next_tool["bonus_percent"]
        self._session.add(state.stats)
        self._session.flush()

        message = f"Інструмент покращено до рівня {next_tool['level']}."
        refreshed = self.get_farm_state(player_id)
        return refreshed, message

    # --- internal helpers -------------------------------------------------

    def _load_player(self, player_id: int) -> Player:
        stmt = (
            select(Player)
            .where(Player.id == player_id)
            .options(
                joinedload(Player.farming_stats),
                joinedload(Player.wallet),
                joinedload(Player.farm_plots).joinedload(FarmPlot.crop).joinedload(PlantedCrop.plant_type),
            )
        )
        result = self._session.execute(stmt)
        player = result.scalars().first()
        if player is None:
            player = Player(
                id=player_id,
                username=None,
                level=1,
                xp=0,
                energy=20,
                max_energy=20,
                gold=0,
            )
            self._session.add(player)
            self._session.flush()
        return player

    def _ensure_stats(self, player: Player) -> PlayerFarmingStats:
        stats = player.farming_stats
        if stats is None:
            stats = PlayerFarmingStats(
                player_id=player.id,
                last_energy_refill_at=datetime.now(timezone.utc),
                starter_seed_charges=1,
            )
            self._session.add(stats)
            self._session.flush()
            player.farming_stats = stats
        elif stats.last_energy_refill_at is None:
            stats.last_energy_refill_at = datetime.now(timezone.utc)
            self._session.add(stats)
        if stats.starter_seed_charges is None:
            stats.starter_seed_charges = 1
            self._session.add(stats)
        return stats

    def _ensure_plots(self, player: Player) -> List[FarmPlot]:
        plots = sorted(player.farm_plots or [], key=lambda p: p.slot_index)
        if len(plots) >= BASE_PLOTS:
            return plots

        for slot in range(1, TOTAL_PLOTS + 1):
            plot = next((p for p in plots if p.slot_index == slot), None)
            if plot is None:
                plot = FarmPlot(
                    player_id=player.id,
                    slot_index=slot,
                    unlocked=True if slot <= BASE_PLOTS else False,
                    unlock_cost=BASE_PLOT_UNLOCK_COST + (slot - BASE_PLOTS) * 250,
                    unlock_level_requirement=max(1, slot),
                    unlock_farming_level_requirement=max(1, slot // 2 + 1),
                )
                if slot <= BASE_PLOTS:
                    plot.unlock_cost = 0
                    plot.unlock_level_requirement = 1
                    plot.unlock_farming_level_requirement = 1
                    plot.unlocked = True
                else:
                    plot.unlocked = False
                self._session.add(plot)
                plots.append(plot)

        plots.sort(key=lambda p: p.slot_index)
        self._session.flush()
        return plots

    def _update_crop_states(self, plots: Iterable[FarmPlot], now: datetime) -> None:
        for plot in plots:
            if plot.crop:
                plot.crop.mark_ready(now)

    def _ensure_default_plants(self) -> List[PlantType]:
        existing = self._session.execute(select(PlantType).order_by(PlantType.id))
        plants = existing.scalars().all()
        if plants:
            return list(plants)

        created: List[PlantType] = []
        for plant_data in DEFAULT_PLANTS:
            plant = PlantType(**plant_data)
            self._session.add(plant)
            created.append(plant)
        self._session.flush()
        return created

    def _apply_tool_bonus(self, base_seconds: int, bonus_percent: int) -> int:
        if bonus_percent <= 0:
            return base_seconds
        reduction = base_seconds * bonus_percent // 100
        adjusted = max(60, base_seconds - reduction)
        return adjusted

    def _guard_plant_requirements(
        self,
        player: Player,
        stats: PlayerFarmingStats,
        plant_type: PlantType,
    ) -> None:
        if player.level < plant_type.unlock_level or stats.level < plant_type.unlock_farming_level:
            raise FarmPlantLocked("Ця культура поки що недоступна.")

    def _spend_energy(self, stats: PlayerFarmingStats, amount: int, now: datetime) -> None:
        if stats.energy < amount:
            raise NotEnoughFarmEnergy("Недостатньо енергії для цієї дії.")
        stats.energy -= amount
        stats.last_energy_refill_at = now
        self._session.add(stats)

    def _plot_by_id(self, plots: Iterable[FarmPlot], plot_id: int) -> FarmPlot:
        for plot in plots:
            if plot.id == plot_id:
                return plot
        raise FarmPlotLocked("Не знайдено ділянки з таким ідентифікатором.")

    def _plant_by_id(self, plants: Iterable[PlantType], plant_id: int) -> PlantType:
        for plant in plants:
            if plant.id == plant_id:
                return plant
        raise FarmPlantLocked("Рослина не знайдена.")

    def _grant_farming_xp(self, stats: PlayerFarmingStats, amount: int) -> Tuple[int, int]:
        if amount <= 0:
            return 0, 0

        stats.xp += amount
        levels_gained = 0
        while stats.xp >= self._xp_required_for_next_level(stats.level):
            stats.xp -= self._xp_required_for_next_level(stats.level)
            stats.level += 1
            levels_gained += 1
            stats.max_energy = min(FARM_ENERGY_MAX_CAP, stats.max_energy + 2)
            stats.energy = min(stats.max_energy, stats.energy + 2)
        self._session.add(stats)
        return amount, levels_gained

    def _xp_required_for_next_level(self, level: int) -> int:
        threshold = FARM_XP_BASE_THRESHOLD * (FARM_XP_GROWTH_FACTOR ** (level - 1))
        return max(10, int(threshold))

    def _ensure_wallet(self, player: Player) -> Wallet:
        wallet = player.wallet
        if wallet is None:
            wallet = Wallet(player_id=player.id, gold=player.gold)
            self._session.add(wallet)
            self._session.flush()
            player.wallet = wallet
        return wallet

    def _find_tool_upgrade(self, tool_level: int) -> Optional[Dict[str, object]]:
        for upgrade in TOOL_UPGRADES:
            if upgrade["level"] == tool_level:
                return upgrade
        return None

    def _apply_passive_energy_regen(self, stats: PlayerFarmingStats, now: datetime) -> None:
        if stats.energy >= stats.max_energy:
            stats.last_energy_refill_at = now
            self._session.add(stats)
            return

        last_update = stats.last_energy_refill_at
        if last_update is None:
            stats.last_energy_refill_at = now
            self._session.add(stats)
            return

        if last_update.tzinfo is None:
            last_update = last_update.replace(tzinfo=timezone.utc)

        elapsed_seconds = (now - last_update).total_seconds()
        if elapsed_seconds < FARM_ENERGY_REGEN_SECONDS:
            return

        energy_points = int(elapsed_seconds // FARM_ENERGY_REGEN_SECONDS)
        if energy_points <= 0:
            return

        stats.energy = min(stats.max_energy, stats.energy + energy_points)
        consumed_seconds = energy_points * FARM_ENERGY_REGEN_SECONDS
        stats.last_energy_refill_at = last_update + timedelta(seconds=consumed_seconds)
        if stats.energy >= stats.max_energy:
            stats.last_energy_refill_at = now
        self._session.add(stats)

    def build_public_state(self, data: FarmStateData) -> Dict[str, object]:
        """Convert internal state into JSON-ready payload."""
        xp_to_next = self._xp_required_for_next_level(data.stats.level)
        plots_public: List[Dict[str, object]] = []
        for plot in data.plots:
            crop_public: Optional[Dict[str, object]] = None
            if plot.crop:
                plant = plot.crop.plant_type
                crop_public = {
                    "id": plot.crop.id,
                    "planted_at": plot.crop.planted_at,
                    "ready_at": plot.crop.ready_at,
                    "state": plot.crop.state,
                    "plant_type": self._plant_public(plant, data.player, data.stats),
                }
            plots_public.append(
                {
                    "id": plot.id,
                    "slot_index": plot.slot_index,
                    "unlocked": plot.unlocked,
                    "unlock_cost": plot.unlock_cost,
                    "unlock_level_requirement": plot.unlock_level_requirement,
                    "unlock_farming_level_requirement": plot.unlock_farming_level_requirement,
                    "crop": crop_public,
                }
            )

        return {
            "player_id": data.player.id,
            "stats": {
                "level": data.stats.level,
                "xp": data.stats.xp,
                "xp_to_next_level": xp_to_next,
                "energy": data.stats.energy,
                "max_energy": data.stats.max_energy,
                "tool": {
                    "level": data.stats.tool_level,
                    "name": data.stats.tool_name,
                    "bonus_percent": data.stats.tool_bonus_percent,
                },
                "starter_seed_charges": data.stats.starter_seed_charges,
            },
            "plots": plots_public,
            "available_plants": [self._plant_public(plant, data.player, data.stats) for plant in data.plants],
            "wallet_gold": data.wallet.gold,
        }

    def _plant_public(self, plant: PlantType, player: Player, stats: PlayerFarmingStats) -> Dict[str, object]:
        return {
            "id": plant.id,
            "name": plant.name,
            "description": plant.description,
            "growth_seconds": plant.growth_seconds,
            "xp_reward": plant.xp_reward,
            "energy_cost": plant.energy_cost,
            "seed_cost": plant.seed_cost,
            "sell_price": plant.sell_price,
            "unlock_level": plant.unlock_level,
            "unlock_farming_level": plant.unlock_farming_level,
            "icon": plant.icon,
            "is_unlocked": self._is_plant_unlocked(player, stats, plant),
        }

    def _is_plant_unlocked(self, player: Player, stats: PlayerFarmingStats, plant: PlantType) -> bool:
        return player.level >= plant.unlock_level and stats.level >= plant.unlock_farming_level
