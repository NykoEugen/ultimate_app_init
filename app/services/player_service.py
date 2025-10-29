from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.player import Player


async def create_player_if_not_exists(session: AsyncSession, player_id: int) -> Player:
    """Fetch player by id or create a new record with default stats."""
    player = await session.get(Player, player_id)
    if player is not None:
        return player

    player = Player(
        id=player_id,
        level=1,
        xp=0,
        energy=20,
        max_energy=20,
        gold=0,
    )
    session.add(player)
    await session.flush()

    return player
