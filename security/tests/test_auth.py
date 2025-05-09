import pytest
import data.db_connect as dbc
import data.people as ppl
from security.auth import register_user, authenticate_user

TEST_USER = "test_user@example.com"
TEST_PASSWORD = "mypassword"
TEST_NAME = "Test Name"

INVALID_USER = "unknown_user@example.com"
INVALID_PASSWORD = "wrongpassword"


@pytest.fixture(scope='function')
def temp_user():
    """
    Creates 'test_user@example.com' by calling register_user(...)
    then yields that user. After the test, it cleans up by deleting
    from the 'people' collection in 'journalDB'.
    """
    created = register_user(TEST_USER, TEST_PASSWORD, TEST_NAME)
    print("temp_user created:", created)
    yield TEST_USER
    try:
        ppl.delete(TEST_USER)
    except:
        print('Person already deleted.')


def test_register_user():
    """
    Test registering a new user (ALT_USER).
    register_user should return True if success, False if user already exists.
    """
    assert not ppl.exists(TEST_USER)
    status = register_user(TEST_USER, TEST_PASSWORD, TEST_NAME)
    assert status is True, "Expected True on successful registration"
    assert ppl.exists(TEST_USER)
    ppl.delete(TEST_USER)


def test_register_duplicate_user(temp_user):
    """
    Ensure duplicate user registration fails.
    The fixture already created TEST_USER, so we expect False now.
    """
    created_again = register_user(temp_user, 'Not Care', 'Not Care')
    assert created_again is False, "Expected False when re-registering same user"


@pytest.mark.parametrize("username, password, expected", [
    (TEST_USER, TEST_PASSWORD, True),
    (TEST_USER, INVALID_PASSWORD, False),
    (INVALID_USER, TEST_PASSWORD, False)
])
def test_authenticate_user(temp_user, username, password, expected):
    """
    authenticate_user returns:
      - dict (like {'email': ..., 'roles': [...], ...}) if success
      - None if fail

    We interpret 'dict => True' and 'None => False', then compare with 'expected'.
    """
    result = authenticate_user(username, password)
    is_success = (result is not None)
    assert is_success == expected, (
        f"For user={username} with password={password}, "
        f"got {result}, expected success={expected}"
    )


def test_authenticate_non_existent_user():
    """
    Additional check for a user we never registered.
    Should return None => fail => interpret as False.
    """
    result = authenticate_user(INVALID_USER, INVALID_PASSWORD)
    assert result is None, "Expected None for non-existent user"
