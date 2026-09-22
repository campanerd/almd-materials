import pytest

from src.database.database_connection import create_database_connection


@pytest.fixture
def db_connection():
    connection = create_database_connection(":memory:")
    yield connection
    connection.close()
