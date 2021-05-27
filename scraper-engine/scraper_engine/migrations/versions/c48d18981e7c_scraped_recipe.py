"""scraped recipe

Revision ID: c48d18981e7c
Revises: 1c250c505256
Create Date: 2021-05-27 23:04:06.448802

"""
from alembic import op
import sqlalchemy as sa

from datetime import datetime

# revision identifiers, used by Alembic.
revision = "c48d18981e7c"
down_revision = "1c250c505256"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "scraped_recipe",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("url", sa.String(255), nullable=False, unique=True),
        sa.Column("json_data", sa.UnicodeText()),
        sa.Column("title", sa.Unicode(255)),
        sa.Column("servings", sa.Unicode(50)),
        sa.Column("total_cooking_time", sa.Unicode(50)),
        sa.Column("author_name", sa.Unicode(50)),
        sa.Column("picture_count", sa.Integer),
        sa.Column("directions_count", sa.Integer),
        sa.Column("ingredients_count", sa.Integer),
        sa.Column("total_ratings", sa.Integer),
        sa.Column("rating", sa.Numeric),
        sa.Column("created_at", sa.DateTime, default=datetime.utcnow),
        sa.Column("updated_at", sa.DateTime, default=datetime.utcnow),
    )


def downgrade():
    op.drop_table("scraped_recipe")
