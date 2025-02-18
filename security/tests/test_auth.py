import pytest
import security.db_connect as dbc
from auth import register_user, authenticate_user

SECURITY_DB = 'securityDB'
USER_COLLECTION = 'users'

TEST_USER = "test_user"
TEST_PASSWORD = "mypassword"

ALT_USER = "alt_user"
ALT_PASSWORD = "altpassword"

INVALID_USER = "unknown_user"
INVALID_PASSWORD = "wrongpassword"


@pytest.fixture(scope='function')
def temp_user():
    """Fixture to create a temporary user for testing."""
    register_user(TEST_USER, TEST_PASSWORD)
    yield TEST_USER
    dbc.connect_db()[SECURITY_DB][USER_COLLECTION].delete_one({'_id': TEST_USER})


def test_register_user():
    """Test registering a new user."""
    assert register_user(ALT_USER, ALT_PASSWORD)
    dbc.connect_db()[SECURITY_DB][USER_COLLECTION].delete_one({'_id': ALT_USER})  # Cleanup


def test_register_duplicate_user(temp_user):
    """Ensure duplicate user registration fails."""
    assert not register_user(TEST_USER, TEST_PASSWORD)


@pytest.mark.parametrize("username, password, expected", [
    (TEST_USER, TEST_PASSWORD, True),  # ✅ Correct credentials
    (TEST_USER, INVALID_PASSWORD, False),  # ❌ Wrong password
    (INVALID_USER, TEST_PASSWORD, False)  # ❌ User does not exist
])
def test_authenticate_user(temp_user, username, password, expected):
    """Test multiple login cases using parameterization."""
    assert authenticate_user(username, password) == expected


def test_authenticate_non_existent_user():
    """Ensure non-existent users cannot authenticate."""
    assert not authenticate_user(INVALID_USER, INVALID_PASSWORD)
