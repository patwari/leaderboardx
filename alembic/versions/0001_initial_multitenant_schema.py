"""initial multitenant schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-01-01
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("company_id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("company_secret", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_companies_company_id", "companies", ["company_id"])
    op.create_index("ix_companies_company_secret", "companies", ["company_secret"], unique=True)

    op.create_table(
        "games",
        sa.Column("game_id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.company_id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("game_secret", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_games_game_id", "games", ["game_id"])
    op.create_index("ix_games_company_id", "games", ["company_id"])
    op.create_index("ix_games_game_secret", "games", ["game_secret"], unique=True)
    op.create_index("ix_games_company_id_name", "games", ["company_id", "name"])

    op.create_table(
        "leaderboards",
        sa.Column("leaderboard_pk", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("game_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("games.game_id", ondelete="CASCADE"), nullable=False),
        sa.Column("leaderboard_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=True),
        sa.Column("sort_order", sa.String(length=4), nullable=False, server_default="desc"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(r"leaderboard_id ~ '^[A-Za-z0-9\\-]+$'", name="check_leaderboard_id_format"),
        sa.CheckConstraint("sort_order IN ('asc','desc')", name="check_sort_order"),
    )
    op.create_index("ix_leaderboards_leaderboard_pk", "leaderboards", ["leaderboard_pk"])
    op.create_index("ix_leaderboards_game_id", "leaderboards", ["game_id"])
    op.create_index("ux_leaderboards_game_id_leaderboard_id", "leaderboards", ["game_id", "leaderboard_id"], unique=True)

    op.create_table(
        "players",
        sa.Column("xid", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("game_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("games.game_id", ondelete="CASCADE"), nullable=False),
        sa.Column("device_id", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(r"device_id ~ '^[A-Za-z0-9\\-]+$'", name="check_device_id_format"),
    )
    op.create_index("ix_players_xid", "players", ["xid"])
    op.create_index("ix_players_game_id", "players", ["game_id"])
    op.create_index("ux_players_game_id_device_id", "players", ["game_id", "device_id"], unique=True)

    op.create_table(
        "player_leaderboard_best",
        sa.Column("leaderboard_pk", postgresql.UUID(as_uuid=True), sa.ForeignKey("leaderboards.leaderboard_pk", ondelete="CASCADE"), primary_key=True, nullable=False),
        sa.Column("player_xid", postgresql.UUID(as_uuid=True), sa.ForeignKey("players.xid", ondelete="CASCADE"), primary_key=True, nullable=False),
        sa.Column("best_value", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_best_scores_leaderboard", "player_leaderboard_best", ["leaderboard_pk"])
    op.create_index("ix_best_scores_player", "player_leaderboard_best", ["player_xid"])

    op.create_table(
        "score_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("leaderboard_pk", postgresql.UUID(as_uuid=True), sa.ForeignKey("leaderboards.leaderboard_pk", ondelete="CASCADE"), nullable=False),
        sa.Column("player_xid", postgresql.UUID(as_uuid=True), sa.ForeignKey("players.xid", ondelete="CASCADE"), nullable=False),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_score_events_leaderboard_pk", "score_events", ["leaderboard_pk"])
    op.create_index("ix_score_events_player_xid", "score_events", ["player_xid"])
    op.create_index("ix_score_events_leaderboard_time", "score_events", ["leaderboard_pk", "submitted_at"])
    op.create_index("ix_score_events_player_time", "score_events", ["player_xid", "submitted_at"])


def downgrade() -> None:
    op.drop_table("score_events")
    op.drop_table("player_leaderboard_best")
    op.drop_table("players")
    op.drop_table("leaderboards")
    op.drop_table("games")
    op.drop_table("companies")