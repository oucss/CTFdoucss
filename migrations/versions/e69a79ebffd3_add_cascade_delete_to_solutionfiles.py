"""Add cascade delete to SolutionFiles

Revision ID: e69a79ebffd3
Revises: 336b8c601b94
Create Date: 2026-07-14 22:16:45.249559

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e69a79ebffd3"
down_revision = "336b8c601b94"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    url = str(bind.engine.url)
    if url.startswith("mysql"):
        existing = bind.execute(
            sa.text("""
                SELECT CONSTRAINT_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'files'
                  AND COLUMN_NAME = 'solution_id'
                  AND REFERENCED_TABLE_NAME = 'solutions'
                  AND REFERENCED_COLUMN_NAME = 'id'
            """)
        ).fetchall()

        if len(existing) > 1:
            raise RuntimeError("Multiple solution foreign keys found on files")

        if existing:
            op.drop_constraint(existing[0][0], "files", type_="foreignkey")

        op.create_foreign_key(
            "files_ibfk_3",
            "files",
            "solutions",
            ["solution_id"],
            ["id"],
            ondelete="CASCADE",
        )
    elif url.startswith("postgres"):
        op.drop_constraint("files_solution_id_fkey", "files", type_="foreignkey")
        op.create_foreign_key(
            "files_solution_id_fkey",
            "files",
            "solutions",
            ["solution_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade():
    bind = op.get_bind()
    url = str(bind.engine.url)
    if url.startswith("mysql"):
        op.drop_constraint("files_ibfk_3", "files", type_="foreignkey")
        op.create_foreign_key(
            "files_ibfk_3", "files", "solutions", ["solution_id"], ["id"]
        )
    elif url.startswith("postgres"):
        op.drop_constraint("files_solution_id_fkey", "files", type_="foreignkey")
        op.create_foreign_key(
            "files_solution_id_fkey", "files", "solutions", ["solution_id"], ["id"]
        )
