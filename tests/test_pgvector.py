from sqlalchemy import text

from app.db.database import engine


def test_pgvector_extension():
    with engine.connect() as connection:
        result = connection.execute(
            text(
                """
                SELECT extversion
                FROM pg_extension
                WHERE extname = 'vector'
                """
            )
        )

        version = result.scalar()

        assert version == "0.8.7"