from __future__ import annotations

from typing import List

from app.db.models.inventory import InventoryItem
from app.db.models.player import Player
from app.schemas.player import InventoryItemPublic, PlayerProfile


def build_player_profile(player: Player) -> PlayerProfile:
    inventory_items: List[InventoryItem] = list(player.inventory_items or [])

    inventory_public = [
        InventoryItemPublic(
            id=item.id,
            name=item.catalog_item.name if item.catalog_item else "Невідомий предмет",
            slot=item.catalog_item.slot if item.catalog_item else "misc",
            rarity=item.catalog_item.rarity if item.catalog_item else "common",
            cosmetic=item.catalog_item.cosmetic if item.catalog_item else False,
            is_equipped=item.is_equipped,
            icon=item.catalog_item.icon if item.catalog_item else None,
            description=item.catalog_item.description if item.catalog_item else None,
        )
        for item in inventory_items
    ]

    wallet_gold = player.wallet.gold if player.wallet else getattr(player, "gold", 0)

    return PlayerProfile(
        player_id=player.id,
        username=player.username,
        level=player.level,
        xp=player.xp,
        energy=player.energy,
        max_energy=player.max_energy,
        gold=wallet_gold,
        last_daily_claim_at=player.last_daily_claim_at,
        inventory=inventory_public,
    )
