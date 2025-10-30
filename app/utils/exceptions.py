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
