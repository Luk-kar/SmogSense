"""
This module contains a context manager to handle database sessions.
"""

# Python
from contextlib import contextmanager

# Dagster
from dagster import (
    Failure,
)

# SQLAlchemy
from sqlalchemy.orm import sessionmaker


@contextmanager
def get_database_session(context):
    """Context manager to handle database sessions."""
    engine = context.resources.postgres_alchemy
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise Failure(
            f"An error occurred during the session. Changes were rolled back:\n{e}"
        ) from e
    finally:
        session.close()
