"""seed_initial_roles

Revision ID: 9288eb0ff771
Revises: 578809f4ac7e
Create Date: 2026-09-09 15:45:13.648144

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9288eb0ff771'
down_revision: Union[str, Sequence[str], None] = '578809f4ac7e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Seed initial roles
    op.execute(
        """
        INSERT INTO roles (id, name, description)
        VALUES 
            (gen_random_uuid(), 'Admin', 'System administrator with full access'),
            (gen_random_uuid(), 'Investigator', 'Investigator analyzing cases'),
            (gen_random_uuid(), 'Analyst', 'Analyst viewing graph data')
        ON CONFLICT (name) DO NOTHING;
        """
    )


def downgrade() -> None:
    # Remove seeded roles
    op.execute(
        """
        DELETE FROM roles WHERE name IN ('Admin', 'Investigator', 'Analyst');
        """
    )
