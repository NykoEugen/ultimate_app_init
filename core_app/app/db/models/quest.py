from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Quest(Base):
    __tablename__ = "quests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_repeatable = Column(Boolean, default=False, nullable=False)

    nodes = relationship("QuestNode", back_populates="quest")

class QuestNode(Base):
    __tablename__ = "quest_nodes"

    id = Column(String, primary_key=True, index=True)
    quest_id = Column(Integer, ForeignKey("quests.id"), nullable=False)

    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)

    is_start = Column(Boolean, default=False, nullable=False)
    is_final = Column(Boolean, default=False, nullable=False)

    quest = relationship("Quest", back_populates="nodes")
    choices = relationship("QuestChoice", back_populates="node")

class QuestChoice(Base):
    __tablename__ = "quest_choices"

    id = Column(String, primary_key=True, index=True)
    node_id = Column(String, ForeignKey("quest_nodes.id"), nullable=False)

    label = Column(String, nullable=False)  # Текст кнопки типу "Допомогти селянам"
    next_node_id = Column(String, nullable=True)  # Куди перейти після вибору

    reward_xp = Column(Integer, default=0, nullable=False)
    reward_item_id = Column(Integer, ForeignKey("inventory_items_catalog.id"), nullable=True)
    # item з каталогу, який можна видати

    node = relationship("QuestNode", back_populates="choices")

class QuestProgress(Base):
    __tablename__ = "quest_progress"

    player_id = Column(Integer, ForeignKey("players.id"), primary_key=True)
    quest_id = Column(Integer, ForeignKey("quests.id"), nullable=False)
    current_node_id = Column(String, ForeignKey("quest_nodes.id"), nullable=False)

    player = relationship("Player", back_populates="quest_progress")
