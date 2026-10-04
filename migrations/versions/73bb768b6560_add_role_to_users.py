"""Add role to users

Revision ID: 73bb768b6560
Revises: 53e9928620e1
Create Date: 2026-10-04 13:22:12.455395

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '73bb768b6560'
down_revision: Union[str, Sequence[str], None] = '53e9928620e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    user_role = sa.Enum(
        'client',
        'admin',
        'provider',
        'tailor',
        name='user_role'
    )

    user_role.create(op.get_bind(), checkfirst=True)

    op.add_column(
        'users',
        sa.Column(
            'role',
            user_role,
            server_default='client',
            nullable=False
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'role')

    user_role = sa.Enum(
        'client',
        'admin',
        'provider',
        'tailor',
        name='user_role'
    )

    user_role.drop(op.get_bind(), checkfirst=True)