import os
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Safety barrier: Force test database environment variable BEFORE any app imports
os.environ["POSTGRES_DB"] = "tracex_test"

from backend.app.core.config import settings
from backend.app.core.postgres import Base, get_db, DATABASE_URL

# Double-check safety barrier
def pytest_configure(config):
    if settings.postgres_db != "tracex_test":
        pytest.exit("CRITICAL ERROR: Tests must run against tracex_test database, not the dev database!")

# Re-create engine explicitly pointing to the test DB just in case
test_engine = create_engine(DATABASE_URL, pool_pre_ping=True)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    from alembic.config import Config
    from alembic import command
    from sqlalchemy import text
    
    # Drop schema to ensure clean state and all triggers are removed
    with test_engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
        conn.commit()

    # Run alembic migrations to recreate tables and triggers
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    
    yield
    # We do NOT drop_all here to allow inspection if tests fail

@pytest.fixture(scope="function")
def db_session():
    """
    Function-scoped fixture that provides a transactional Session.
    Any commits inside the test will only flush to the savepoint.
    The entire transaction is rolled back at the end of the test.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function", autouse=True)
def override_get_db_dependency(db_session):
    from backend.app.main import app
    app.dependency_overrides[get_db] = lambda: db_session
    yield
    app.dependency_overrides.pop(get_db, None)

@pytest.fixture(scope="function", autouse=True)
def mock_neo4j_driver(request):
    """
    Prevent accidental mutations to the primary development graph database.
    Mocks the global Neo4j driver for all tests by default.
    Unless the test is explicitly marked as 'e2e' (where we would use a separate graph db)
    """
    if "e2e" in request.keywords:
        yield None
        return
        
    with patch("backend.app.graph.engine.driver") as mock_driver:
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        yield mock_session
