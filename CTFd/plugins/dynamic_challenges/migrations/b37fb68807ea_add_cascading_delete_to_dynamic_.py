"""Add cascading delete to dynamic challenges

Revision ID: b37fb68807ea
Revises:
Create Date: 2020-05-06 12:21:39.373983

"""

import sqlalchemy

revision = "b37fb68807ea"
down_revision = None
branch_labels = None
depends_on = None


def upgrade(op=None):
    bind = op.get_bind()
    url = str(bind.engine.url)

    if url.startswith("mysql"):
        existing = bind.execute(
            sqlalchemy.text("""
                SELECT CONSTRAINT_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'dynamic_challenge'
                  AND COLUMN_NAME = 'id'
                  AND REFERENCED_TABLE_NAME = 'challenges'
                  AND REFERENCED_COLUMN_NAME = 'id'
            """)
        ).fetchall()

        if len(existing) > 1:
            raise RuntimeError(
                "Multiple foreign keys found on dynamic_challenge.id"
            )

        if existing:
            op.drop_constraint(
                existing[0][0],
                "dynamic_challenge",
                type_="foreignkey",
            )

        op.create_foreign_key(
            "dynamic_challenge_ibfk_1",
            "dynamic_challenge",
            "challenges",
            ["id"],
            ["id"],
            ondelete="CASCADE",
        )

    elif url.startswith("postgres"):
        try:
            op.drop_constraint(
                "dynamic_challenge_id_fkey",
                "dynamic_challenge",
                type_="foreignkey",
            )
        except sqlalchemy.exc.InternalError as e:
            print(str(e))

        try:
            op.create_foreign_key(
                None,
                "dynamic_challenge",
                "challenges",
                ["id"],
                ["id"],
                ondelete="CASCADE",
            )
        except sqlalchemy.exc.InternalError as e:
            print(str(e))


def downgrade(op=None):
    bind = op.get_bind()
    url = str(bind.engine.url)
    try:
        if url.startswith("mysql"):
            op.drop_constraint(
                "dynamic_challenge_ibfk_1", "dynamic_challenge", type_="foreignkey"
            )
        elif url.startswith("postgres"):
            op.drop_constraint(
                "dynamic_challenge_id_fkey", "dynamic_challenge", type_="foreignkey"
            )
    except sqlalchemy.exc.InternalError as e:
        print(str(e))

    try:
        op.create_foreign_key(None, "dynamic_challenge", "challenges", ["id"], ["id"])
    except sqlalchemy.exc.InternalError as e:
        print(str(e))
