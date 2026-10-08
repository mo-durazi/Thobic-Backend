"""Add Cloudinary photo metadata to profiles.

Revision ID: d8a4c1f09b72
Revises: c4930e29d13e
Create Date: 2026-10-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d8a4c1f09b72"
down_revision: Union[str, Sequence[str], None] = "c4930e29d13e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("profiles", sa.Column("shop_photo_url", sa.String(), nullable=True))
    op.add_column("profiles", sa.Column("shop_photo_public_id", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("profiles", "shop_photo_public_id")
    op.drop_column("profiles", "shop_photo_url")
