from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.player_stats import DEFAULT_BASE_STATS
from app.db.models.player import Player
from app.db.models.wallet import Wallet


async def create_player_if_not_exists(session: AsyncSession, player_id: int) -> Player:
    """Fetch player by id or create a new record with default stats."""
    player = await session.get(Player, player_id)
    if player is None:
        player = Player(
            id=player_id,
            level=1,
            xp=0,
            energy=20,
            max_energy=20,
            gold=0,
            **DEFAULT_BASE_STATS,
        )
        session.add(player)
        await session.flush()

    wallet = await session.get(Wallet, player.id)
    if wallet is None:
        wallet = Wallet(player_id=player.id, gold=player.gold)
        session.add(wallet)
        await session.flush()
    else:
        wallet.gold = player.gold

    return player
