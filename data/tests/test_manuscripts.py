import pytest
import random
import data.manuscript as mss


TEST_TITLE = "Test Manuscript Title"
TEST_AUTHOR = "John Doe"
TEMP_TITLE = "temp_manuscript_title"
TEMP_AUTHOR = "temp_author@univ.edu"
BAD_TITLE = "   "
BAD_AUTHOR = "   "
TEST_REFEREE = "jane.ref@example.com"
BAD_REFEREE = "   "


# Example actions and states for testing:
TEST_VALID_STATE = mss.TEST_STATE
TEST_VALID_ACTION = mss.ASSIGN_REF
TEST_INVALID_STATE = "NOT_A_VALID_STATE"
TEST_INVALID_ACTION = "NOT_A_VALID_ACTION"


@pytest.fixture(scope='function')
def temp_manuscript():
    # Create a temporary manuscript and yield its title
    title = mss.create(TEMP_TITLE, TEMP_AUTHOR)
    yield title
    # Attempt to delete after test
    try:
        mss.delete(title)
    except:
        print('Manuscript already deleted or not found.')


def gen_random_not_valid_str() -> str:
    BIG_NUM = 10_000_000_000
    big_int = random.randint(0, BIG_NUM)
    big_int += BIG_NUM
    bad_str = str(big_int)
    return bad_str


def test_create():
    assert not mss.exists(TEST_TITLE)
    title = mss.create(TEST_TITLE, TEST_AUTHOR)
    assert mss.exists(TEST_TITLE)
    # Cleanup
    mss.delete(TEST_TITLE)


def test_create_duplicate(temp_manuscript):
    with pytest.raises(ValueError):
        mss.create(TEMP_TITLE, "Another Author")


def test_create_empty_title():
    with pytest.raises(ValueError):
        mss.create(BAD_TITLE, TEST_AUTHOR)


def test_create_empty_author():
    with pytest.raises(ValueError):
        mss.create(TEST_TITLE, BAD_AUTHOR)
    # Just in case it created something, but it should not.
    if mss.exists(TEST_TITLE):
        mss.delete(TEST_TITLE)


def test_exists(temp_manuscript):
    assert mss.exists(temp_manuscript)


def test_doesnt_exist():
    assert not mss.exists("Non_Existent_Title_1234")


def test_read(temp_manuscript):
    manuscripts = mss.read()
    assert isinstance(manuscripts, dict)
    assert len(manuscripts) > 0
    # check for string keys and presence of expected fields
    for title, manuscript in manuscripts.items():
        assert isinstance(title, str)
        assert mss.TITLE in manuscript
        assert mss.AUTHOR in manuscript
        assert mss.REFEREES in manuscript
        assert mss.STATE in manuscript


def test_read_one(temp_manuscript):
    manu = mss.read_one(temp_manuscript)
    assert manu is not None
    assert manu[mss.TITLE] == temp_manuscript


def test_read_one_not_there():
    assert mss.read_one("Non_Existent_Title_999") is None


def test_delete(temp_manuscript):
    mss.delete(temp_manuscript)
    assert not mss.exists(temp_manuscript)


@pytest.fixture(scope='function')
def temp_manuscript_for_update():
    title = mss.create(TEST_TITLE, TEST_AUTHOR)
    yield title
    try:
        mss.delete(title)
    except:
        pass


def test_update_blank_value(temp_manuscript_for_update):
    with pytest.raises(ValueError):
        mss.update(temp_manuscript_for_update, author=BAD_AUTHOR)


def test_update_invalid_title():
    with pytest.raises(ValueError):
        mss.update("invalid title", author="New Author")


def test_update_valid(temp_manuscript_for_update):
    old_author = mss.read_one(temp_manuscript_for_update)[mss.AUTHOR]
    new_author = "Updated Author"
    new_title = mss.update(temp_manuscript_for_update, author=new_author)
    updated_author = mss.read_one(temp_manuscript_for_update)[mss.AUTHOR]
    assert new_title == temp_manuscript_for_update
    assert updated_author != old_author
    assert updated_author == new_author


def test_add_referee(temp_manuscript_for_update):
    old_refs = mss.read_one(temp_manuscript_for_update)[mss.REFEREES]
    assert TEST_REFEREE not in old_refs
    title = mss.add_referee(temp_manuscript_for_update, TEST_REFEREE)
    assert title == temp_manuscript_for_update
    new_refs = mss.read_one(temp_manuscript_for_update)[mss.REFEREES]
    assert TEST_REFEREE in new_refs


def test_add_duplicate_referee(temp_manuscript_for_update):
    mss.add_referee(temp_manuscript_for_update, TEST_REFEREE)
    with pytest.raises(ValueError, match="already exists"):
        mss.add_referee(temp_manuscript_for_update, TEST_REFEREE)


def test_add_referee_blank(temp_manuscript_for_update):
    with pytest.raises(ValueError):
        mss.add_referee(temp_manuscript_for_update, BAD_REFEREE)


def test_add_referee_invalid_title():
    with pytest.raises(ValueError):
        mss.add_referee("invalid title", TEST_REFEREE)


def test_remove_referee(temp_manuscript_for_update):
    mss.add_referee(temp_manuscript_for_update, TEST_REFEREE)
    old_refs = mss.read_one(temp_manuscript_for_update)[mss.REFEREES]
    assert TEST_REFEREE in old_refs
    title = mss.remove_referee(temp_manuscript_for_update, TEST_REFEREE)
    assert title == temp_manuscript_for_update
    new_refs = mss.read_one(temp_manuscript_for_update)[mss.REFEREES]
    assert TEST_REFEREE not in new_refs


def test_remove_not_existing_referee(temp_manuscript_for_update):
    with pytest.raises(ValueError, match="does not exist"):
        mss.remove_referee(temp_manuscript_for_update, TEST_REFEREE)


def test_remove_referee_blank(temp_manuscript_for_update):
    with pytest.raises(ValueError):
        mss.remove_referee(temp_manuscript_for_update, BAD_REFEREE)


def test_remove_referee_invalid_title():
    with pytest.raises(ValueError):
        mss.remove_referee("invalid title", TEST_REFEREE)


@pytest.fixture(scope='function')
def temp_manuscript_for_actions():
    # create a manuscript and add a referee to simulate some states
    title = mss.create("Action Test Title", "Action Author")
    yield title
    try:
        mss.delete(title)
    except:
        pass


def test_handle_action_on_manuscript_invalid_title():
    with pytest.raises(ValueError):
        mss.handle_action_on_manuscript("invalid title", TEST_VALID_ACTION)


def test_handle_action_on_manuscript_invalid_action(temp_manuscript_for_actions):
    with pytest.raises(ValueError):
        mss.handle_action_on_manuscript(temp_manuscript_for_actions, TEST_INVALID_ACTION)


def test_handle_action_on_manuscript_valid(temp_manuscript_for_actions):
    mss.add_referee(temp_manuscript_for_actions, TEST_REFEREE)
    new_state = mss.handle_action_on_manuscript(
        temp_manuscript_for_actions, TEST_VALID_ACTION, referee=TEST_REFEREE
    )
    assert mss.is_valid_state(new_state)


def test_handle_action_on_manuscript_invalid_ref(temp_manuscript_for_actions):
    # For ASSIGN_REF, ref is required. Let's try without it.
    with pytest.raises(ValueError):
        mss.handle_action_on_manuscript(temp_manuscript_for_actions, mss.ASSIGN_REF)


def test_update_invalid_state(temp_manuscript_for_update):
    with pytest.raises(ValueError):
        mss.update(temp_manuscript_for_update, state=TEST_INVALID_STATE)
