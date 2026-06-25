"""
Global pytest setup.

Mock PostgreSQL before test files are imported because
DatabaseSDKFacade opens a PostgreSQL connection during import.
"""

from unittest.mock import MagicMock, patch


postgres_connect_patcher = patch(
    "psycopg2.connect",
    return_value=MagicMock(name="mock_postgres_connection"),
)

postgres_connect_patcher.start()


def pytest_sessionfinish(session, exitstatus):
    postgres_connect_patcher.stop()
