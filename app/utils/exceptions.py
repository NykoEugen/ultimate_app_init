class GameLogicError(Exception):
    """Base class for game specific domain errors."""


class DailyRewardUnavailable(GameLogicError):
    """Daily reward cannot be claimed at the moment."""


class QuestLogicError(GameLogicError):
    """Base class for quest related issues."""


class QuestNotConfigured(QuestLogicError):
    """The quest configuration is incomplete or missing."""


class QuestChoiceInvalid(QuestLogicError):
    """Raised when a player attempts to use an invalid quest choice."""


class QuestNodeNotFound(QuestLogicError):
    """Raised when a quest node referenced by logic cannot be located."""


class InventoryItemNotFound(GameLogicError):
    """Raised when an inventory catalog item cannot be located."""


class ShopOfferUnavailable(GameLogicError):
    """Raised when a shop offer cannot be purchased (expired or already owned)."""


class InsufficientFunds(GameLogicError):
    """Raised when a wallet balance is not enough for the requested purchase."""

    def __init__(self, available: int, required: int) -> None:
        self.available = available
        self.required = required
        super().__init__(f"Not enough gold: need {required}, have {available}")


class FarmPlotLocked(GameLogicError):
    """Raised when attempting to use a locked plot."""


class FarmPlotOccupied(GameLogicError):
    """Raised when attempting to plant on an occupied plot."""


class FarmPlotEmpty(GameLogicError):
    """Raised when attempting to harvest an empty plot."""


class FarmPlantLocked(GameLogicError):
    """Raised when a plant blueprint is not available for the player."""


class NotEnoughFarmEnergy(GameLogicError):
    """Raised when the player lacks farming energy for an action."""


class FarmingToolUpgradeUnavailable(GameLogicError):
    """Raised when the farming tool cannot be upgraded further."""
