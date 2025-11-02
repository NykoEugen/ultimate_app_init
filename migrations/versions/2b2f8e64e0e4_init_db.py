"""init db

Revision ID: 2b2f8e64e0e4
Revises: None
Create Date: 2024-11-01 12:00:00

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2b2f8e64e0e4"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inventory_items_catalog",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slot", sa.String(), nullable=False, server_default="misc"),
        sa.Column("rarity", sa.String(), nullable=False, server_default="common"),
        sa.Column("cosmetic", sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_inventory_items_catalog_id"), "inventory_items_catalog", ["id"], unique=False)

    op.create_table(
        "players",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("energy", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("max_energy", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("gold", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("strength", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("agility", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("intelligence", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("vitality", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("onboarding_completed", sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
        sa.Column("last_daily_claim_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_players_id"), "players", ["id"], unique=False)

    op.create_table(
        "farm_plant_catalog",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("growth_seconds", sa.Integer(), nullable=False, server_default="600"),
        sa.Column("xp_reward", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("energy_cost", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("seed_cost", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sell_price", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unlock_level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("unlock_farming_level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("icon", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_farm_plant_catalog_id"), "farm_plant_catalog", ["id"], unique=False)
    op.create_unique_constraint("uq_farm_plant_catalog_name", "farm_plant_catalog", ["name"])

    op.create_table(
        "quests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_repeatable", sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_quests_id"), "quests", ["id"], unique=False)

    op.create_table(
        "shop_offers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("catalog_item_id", sa.Integer(), nullable=False),
        sa.Column("price_gold", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_limited", sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
        sa.ForeignKeyConstraint(["catalog_item_id"], ["inventory_items_catalog.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "wallets",
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("gold", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ),
        sa.PrimaryKeyConstraint("player_id"),
    )

    op.create_table(
        "farm_player_stats",
        sa.Column("player_id", sa.BigInteger(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("energy", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("max_energy", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("tool_level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("tool_name", sa.String(), nullable=False, server_default="Дерев'яна сапка"),
        sa.Column("tool_bonus_percent", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_energy_refill_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("starter_seed_charges", sa.Integer(), nullable=False, server_default="1"),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ),
        sa.PrimaryKeyConstraint("player_id"),
    )

    op.create_table(
        "inventory_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("catalog_item_id", sa.Integer(), nullable=False),
        sa.Column("is_equipped", sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
        sa.ForeignKeyConstraint(["catalog_item_id"], ["inventory_items_catalog.id"], ),
        sa.ForeignKeyConstraint(["owner_id"], ["players.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_inventory_items_id"), "inventory_items", ["id"], unique=False)

    op.create_table(
        "player_activity_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("activity_type", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_player_activity_log_player_id"), "player_activity_log", ["player_id"], unique=False)

    op.create_table(
        "farm_plots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("player_id", sa.BigInteger(), nullable=False),
        sa.Column("slot_index", sa.Integer(), nullable=False),
        sa.Column("unlocked", sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
        sa.Column("unlock_cost", sa.Integer(), nullable=False, server_default="200"),
        sa.Column("unlock_level_requirement", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("unlock_farming_level_requirement", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_farm_plots_id"), "farm_plots", ["id"], unique=False)
    op.create_index(op.f("ix_farm_plots_player_id"), "farm_plots", ["player_id"], unique=False)

    op.create_table(
        "farm_planted_crops",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("plot_id", sa.Integer(), nullable=False),
        sa.Column("plant_type_id", sa.Integer(), nullable=False),
        sa.Column("planted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("ready_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("harvested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("state", sa.String(), nullable=False, server_default="growing"),
        sa.ForeignKeyConstraint(["plant_type_id"], ["farm_plant_catalog.id"], ),
        sa.ForeignKeyConstraint(["plot_id"], ["farm_plots.id"], ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("plot_id"),
    )
    op.create_index(op.f("ix_farm_planted_crops_id"), "farm_planted_crops", ["id"], unique=False)

    op.create_table(
        "quest_nodes",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("quest_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_start", sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
        sa.Column("is_final", sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
        sa.ForeignKeyConstraint(["quest_id"], ["quests.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_quest_nodes_id"), "quest_nodes", ["id"], unique=False)

    op.create_table(
        "quest_choices",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("node_id", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("next_node_id", sa.String(), nullable=True),
        sa.Column("reward_xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reward_item_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["node_id"], ["quest_nodes.id"], ),
        sa.ForeignKeyConstraint(["reward_item_id"], ["inventory_items_catalog.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_quest_choices_id"), "quest_choices", ["id"], unique=False)

    op.create_table(
        "quest_progress",
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("quest_id", sa.Integer(), nullable=False),
        sa.Column("current_node_id", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["current_node_id"], ["quest_nodes.id"], ),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ),
        sa.ForeignKeyConstraint(["quest_id"], ["quests.id"], ),
        sa.PrimaryKeyConstraint("player_id"),
    )


def downgrade() -> None:
    op.drop_table("quest_progress")
    op.drop_index(op.f("ix_quest_choices_id"), table_name="quest_choices")
    op.drop_table("quest_choices")
    op.drop_index(op.f("ix_quest_nodes_id"), table_name="quest_nodes")
    op.drop_table("quest_nodes")
    op.drop_index(op.f("ix_farm_planted_crops_id"), table_name="farm_planted_crops")
    op.drop_table("farm_planted_crops")
    op.drop_index(op.f("ix_farm_plots_player_id"), table_name="farm_plots")
    op.drop_index(op.f("ix_farm_plots_id"), table_name="farm_plots")
    op.drop_table("farm_plots")
    op.drop_index(op.f("ix_player_activity_log_player_id"), table_name="player_activity_log")
    op.drop_table("player_activity_log")
    op.drop_index(op.f("ix_inventory_items_id"), table_name="inventory_items")
    op.drop_table("inventory_items")
    op.drop_table("farm_player_stats")
    op.drop_table("wallets")
    op.drop_table("shop_offers")
    op.drop_index(op.f("ix_quests_id"), table_name="quests")
    op.drop_table("quests")
    op.drop_unique_constraint("uq_farm_plant_catalog_name", "farm_plant_catalog")
    op.drop_index(op.f("ix_farm_plant_catalog_id"), table_name="farm_plant_catalog")
    op.drop_table("farm_plant_catalog")
    op.drop_index(op.f("ix_players_id"), table_name="players")
    op.drop_table("players")
    op.drop_index(op.f("ix_inventory_items_catalog_id"), table_name="inventory_items_catalog")
    op.drop_table("inventory_items_catalog")
