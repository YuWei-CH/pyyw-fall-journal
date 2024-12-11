import pytest
import random
import data.manuscript as ms


TEST_TITLE = "Test Manuscript Title"
TEST_AUTHOR = "John Doe"
TEMP_TITLE = "temp_manuscript_title"
TEMP_AUTHOR = "temp_author@univ.edu"
BAD_TITLE = "   "
BAD_AUTHOR = "   "
TEST_REFEREE = "jane.ref@example.com"
BAD_REFEREE = "   "


# Example actions and states for testing:
TEST_VALID_STATE = ms.TEST_STATE
TEST_VALID_ACTION = ms.ASSIGN_REF
TEST_INVALID_STATE = "NOT_A_VALID_STATE"
TEST_INVALID_ACTION = "NOT_A_VALID_ACTION"


@pytest.fixture(scope='function')
def temp_manuscript():
    # Create a temporary manuscript and yield its title
    title = ms.create(TEMP_TITLE, TEMP_AUTHOR)
    yield title
    # Attempt to delete after test
    try:
        ms.delete(title)
    except:
        print('Manuscript already deleted or not found.')


def gen_random_not_valid_str() -> str:
    BIG_NUM = 10_000_000_000
    big_int = random.randint(0, BIG_NUM)
    big_int += BIG_NUM
    bad_str = str(big_int)
    return bad_str


def test_create():
    assert not ms.exists(TEST_TITLE)
    title = ms.create(TEST_TITLE, TEST_AUTHOR)
    assert ms.exists(TEST_TITLE)
    # Cleanup
    ms.delete(TEST_TITLE)


def test_create_duplicate(temp_manuscript):
    with pytest.raises(ValueError):
        ms.create(TEMP_TITLE, "Another Author")


def test_create_empty_title():
    with pytest.raises(ValueError):
        ms.create(BAD_TITLE, TEST_AUTHOR)


def test_create_empty_author():
    with pytest.raises(ValueError):
        ms.create(TEST_TITLE, BAD_AUTHOR)
    # Just in case it created something, but it should not.
    if ms.exists(TEST_TITLE):
        ms.delete(TEST_TITLE)


def test_exists(temp_manuscript):
    assert ms.exists(temp_manuscript)


def test_doesnt_exist():
    assert not ms.exists("Non_Existent_Title_1234")


def test_read(temp_manuscript):
    manuscripts = ms.read()
    assert isinstance(manuscripts, dict)
    assert len(manuscripts) > 0
    # check for string keys and presence of expected fields
    for title, manuscript in manuscripts.items():
        assert isinstance(title, str)
        assert ms.TITLE in manuscript
        assert ms.AUTHOR in manuscript
        assert ms.REFEREES in manuscript
        assert ms.STATE in manuscript


def test_read_one(temp_manuscript):
    manu = ms.read_one(temp_manuscript)
    assert manu is not None
    assert manu[ms.TITLE] == temp_manuscript


def test_read_one_not_there():
    assert ms.read_one("Non_Existent_Title_999") is None


def test_delete(temp_manuscript):
    ms.delete(temp_manuscript)
    assert not ms.exists(temp_manuscript)


@pytest.fixture(scope='function')
def temp_manuscript_for_update():
    title = ms.create(TEST_TITLE, TEST_AUTHOR)
    yield title
    try:
        ms.delete(title)
    except:
        pass


def test_update_blank_value(temp_manuscript_for_update):
    with pytest.raises(ValueError):
        ms.update(temp_manuscript_for_update, author=BAD_AUTHOR)


def test_update_invalid_title():
    with pytest.raises(ValueError):
        ms.update("invalid title", author="New Author")


def test_update_valid(temp_manuscript_for_update):
    old_author = ms.read_one(temp_manuscript_for_update)[ms.AUTHOR]
    new_author = "Updated Author"
    new_title = ms.update(temp_manuscript_for_update, author=new_author)
    updated_author = ms.read_one(temp_manuscript_for_update)[ms.AUTHOR]
    assert new_title == temp_manuscript_for_update
    assert updated_author != old_author
    assert updated_author == new_author


def test_add_referee(temp_manuscript_for_update):
    old_refs = ms.read_one(temp_manuscript_for_update)[ms.REFEREES]
    assert TEST_REFEREE not in old_refs
    title = ms.add_referee(temp_manuscript_for_update, TEST_REFEREE)
    assert title == temp_manuscript_for_update
    new_refs = ms.read_one(temp_manuscript_for_update)[ms.REFEREES]
    assert TEST_REFEREE in new_refs


def test_add_duplicate_referee(temp_manuscript_for_update):
    ms.add_referee(temp_manuscript_for_update, TEST_REFEREE)
    with pytest.raises(ValueError, match="already exists"):
        ms.add_referee(temp_manuscript_for_update, TEST_REFEREE)


def test_add_referee_blank(temp_manuscript_for_update):
    with pytest.raises(ValueError):
        ms.add_referee(temp_manuscript_for_update, BAD_REFEREE)


def test_add_referee_invalid_title():
    with pytest.raises(ValueError):
        ms.add_referee("invalid title", TEST_REFEREE)


def test_remove_referee(temp_manuscript_for_update):
    ms.add_referee(temp_manuscript_for_update, TEST_REFEREE)
    old_refs = ms.read_one(temp_manuscript_for_update)[ms.REFEREES]
    assert TEST_REFEREE in old_refs
    title = ms.remove_referee(temp_manuscript_for_update, TEST_REFEREE)
    assert title == temp_manuscript_for_update
    new_refs = ms.read_one(temp_manuscript_for_update)[ms.REFEREES]
    assert TEST_REFEREE not in new_refs


def test_remove_not_existing_referee(temp_manuscript_for_update):
    with pytest.raises(ValueError, match="does not exist"):
        ms.remove_referee(temp_manuscript_for_update, TEST_REFEREE)


def test_remove_referee_blank(temp_manuscript_for_update):
    with pytest.raises(ValueError):
        ms.remove_referee(temp_manuscript_for_update, BAD_REFEREE)


def test_remove_referee_invalid_title():
    with pytest.raises(ValueError):
        ms.remove_referee("invalid title", TEST_REFEREE)


@pytest.fixture(scope='function')
def temp_manuscript_for_actions():
    # create a manuscript and add a referee to simulate some states
    title = ms.create("Action Test Title", "Action Author")
    yield title
    try:
        ms.delete(title)
    except:
        pass


def test_handle_action_on_manuscript_invalid_title():
    with pytest.raises(ValueError):
        ms.handle_action_on_manuscript("invalid title", TEST_VALID_ACTION)


def test_handle_action_on_manuscript_invalid_action(temp_manuscript_for_actions):
    with pytest.raises(ValueError):
        ms.handle_action_on_manuscript(temp_manuscript_for_actions, TEST_INVALID_ACTION)


def test_handle_action_on_manuscript_valid(temp_manuscript_for_actions):
    ms.add_referee(temp_manuscript_for_actions, TEST_REFEREE)
    new_state = ms.handle_action_on_manuscript(
        temp_manuscript_for_actions, TEST_VALID_ACTION, referee=TEST_REFEREE
    )
    assert ms.is_valid_state(new_state)


def test_handle_action_on_manuscript_invalid_ref(temp_manuscript_for_actions):
    # For ASSIGN_REF, ref is required. Let's try without it.
    with pytest.raises(ValueError):
        ms.handle_action_on_manuscript(temp_manuscript_for_actions, ms.ASSIGN_REF)


def test_update_invalid_state(temp_manuscript_for_update):
    with pytest.raises(ValueError):
        ms.update(temp_manuscript_for_update, state=TEST_INVALID_STATE)
