import pytest
import random
import data.manuscript as ms


TEST_TITLE = "Test Manuscript Title"
TEST_AUTHOR = "Test Author"
TEST_REFEREE = "Test Referee"
TEST_AUTHOR_EMAIL = "testAuthor@gmail.com"
TEST_TEXT = "Test Text"
TEST_ABSTRACT = "Test Abstract"
TEST_EDITOR_EMAIL = "testEditor@gmail.com"

TEMP_TITLE = "Temp Manuscript Title"
TEMP_AUTHOR = "Temp Author"
TEMP_AUTHOR_EMAIL = "tempAuthor@gmail.com"
TEMP_TEXT = "Temp Text"
TEMP_ABSTRACT = "Temp Abstract"
TEMP_EDITOR_EMAIL = "tempEditor@gmail.com"

GOOD_EMAIL = "goodemail@gmail.com"
BAD_EMAIL = "bademail"


def gen_random_not_valid_str() -> str:
    BIG_NUM = 10_000_000_000
    big_int = random.randint(0, BIG_NUM)
    big_int += BIG_NUM
    bad_str = str(big_int)
    return bad_str


@pytest.fixture(scope='function')
def temp_manuscript():
    # Create a temporary manuscript and yield its title
    title = ms.create(TEMP_TITLE, TEMP_AUTHOR, TEMP_AUTHOR_EMAIL, 
                      TEMP_TEXT, TEMP_ABSTRACT, TEMP_EDITOR_EMAIL)
    yield title
    # Attempt to delete after test
    try:
        ms.delete(title)
    except:
        print('Manuscript already deleted. ')


def test_is_valid_state():
    for state in ms.get_states():
        assert ms.is_valid_state(state)


def test_is_not_valid_state():
    # run this test "a few" times
    for i in range(10):
        assert not ms.is_valid_state(gen_random_not_valid_str())


def test_is_valid_action():
    for action in ms.get_actions():
        assert ms.is_valid_action(action)


def test_is_not_valid_action():
    # run this test "a few" times
    for i in range(10):
        assert not ms.is_valid_action(gen_random_not_valid_str())


def test_handle_action_bad_state(temp_manuscript):
    with pytest.raises(ValueError):
        ms.handle_action(gen_random_not_valid_str(),
                           ms.TEST_ACTION,
                           manu=ms.read_one(temp_manuscript))


def test_handle_action_bad_action(temp_manuscript):
    with pytest.raises(ValueError):
        ms.handle_action(ms.TEST_STATE,
                           gen_random_not_valid_str(),
                           manu=ms.read_one(temp_manuscript))


def test_handle_action_valid_return(temp_manuscript):
    for state in ms.get_states():
        for action in ms.get_valid_actions_by_state(state):
            print(f'{action=}')
            new_state = ms.handle_action(state, action,
                                         manu=ms.read_one(temp_manuscript),
                                         ref='Some ref')
            print(f'{new_state=}')
            assert ms.is_valid_state(new_state)


def test_create():
    assert not ms.exists(TEST_TITLE)
    ms.create(TEST_TITLE, TEST_AUTHOR, TEST_AUTHOR_EMAIL, 
              TEST_TEXT, TEST_ABSTRACT, TEST_EDITOR_EMAIL)
    assert ms.exists(TEST_TITLE)
    # Cleanup
    ms.delete(TEST_TITLE)


def test_create_duplicate(temp_manuscript):
    with pytest.raises(ValueError):
        ms.create(temp_manuscript, "Do not care about author", 
                  GOOD_EMAIL, "or text", "or abstract", GOOD_EMAIL)


def test_create_empty_title():
    with pytest.raises(ValueError):
        ms.create(" ", "Do not care about author", 
                  GOOD_EMAIL, "or text", "or abstract", GOOD_EMAIL)


def test_create_empty_author():
    with pytest.raises(ValueError):
        ms.create("Do not care about title", " ", 
                  GOOD_EMAIL, "or text", "or abstract", GOOD_EMAIL)


def test_create_empty_text():
    with pytest.raises(ValueError):
        ms.create("Do not care about title", "or author", 
                  GOOD_EMAIL, " ", "or abstract", GOOD_EMAIL)


def test_create_empty_abstract():
    with pytest.raises(ValueError):
        ms.create("Do not care about title", "or author", 
                  GOOD_EMAIL, "or text", " ", GOOD_EMAIL)


def test_create_bad_author_email():
    with pytest.raises(ValueError):
        ms.create("Do not care about title", "or author", 
                  BAD_EMAIL, "or text", "or abstract", GOOD_EMAIL)


def test_create_bad_editor_email():
    with pytest.raises(ValueError):
        ms.create("Do not care about title", "or author", 
                  GOOD_EMAIL, "or text", "or abstract", BAD_EMAIL)


def test_exists(temp_manuscript):
    assert ms.exists(temp_manuscript)


def test_doesnt_exist():
    assert not ms.exists("Not an existing title!")


def test_read(temp_manuscript):
    manuscripts = ms.read()
    assert isinstance(manuscripts, dict)
    assert len(manuscripts) > 0
    # check for string keys and presence of expected fields
    for title, manuscript in manuscripts.items():
        assert isinstance(title, str)
        assert ms.TITLE in manuscript
        assert ms.AUTHOR in manuscript
        assert ms.AUTHOR_EMAIL in manuscript
        assert ms.STATE in manuscript
        assert ms.REFEREES in manuscript
        assert ms.TEXT in manuscript
        assert ms.ABSTRACT in manuscript
        assert ms.HISTORY in manuscript
        assert ms.EDITOR_EMAIL in manuscript


def test_read_one(temp_manuscript):
    assert ms.read_one(temp_manuscript) is not None


def test_read_one_not_there():
    assert ms.read_one("Not an existing title!") is None


def test_delete(temp_manuscript):
    ms.delete(temp_manuscript)
    assert not ms.exists(temp_manuscript)


def test_delete_not_found():
    result = ms.delete('Not an existing title!')
    assert result is None


def test_update_blank_author(temp_manuscript):
    with pytest.raises(ValueError):
        ms.update(temp_manuscript, " ", GOOD_EMAIL, 
                  "Not Care", "Not Care", GOOD_EMAIL)


def test_update_blank_text(temp_manuscript):
    with pytest.raises(ValueError):
        ms.update(temp_manuscript, "Not Care", GOOD_EMAIL, 
                  " ", "Not Care", GOOD_EMAIL)


def test_update_blank_abstract(temp_manuscript):
    with pytest.raises(ValueError):
        ms.update(temp_manuscript, "Not Care", GOOD_EMAIL, 
                  "Not Care", " ", GOOD_EMAIL)


def test_update_invalid_author_email(temp_manuscript):
    with pytest.raises(ValueError):
        ms.update(temp_manuscript, "Not Care", BAD_EMAIL, 
                  "Not Care", "Not Care", GOOD_EMAIL)


def test_update_invalid_editor_email(temp_manuscript):
    with pytest.raises(ValueError):
        ms.update(temp_manuscript, "Not Care", GOOD_EMAIL, 
                  "Not Care", "Not Care", BAD_EMAIL)


def test_update_invalid_title():
    with pytest.raises(ValueError):
        ms.update("invalid title", "Not Care", GOOD_EMAIL, 
                  "Not Care", "Not Care", GOOD_EMAIL)


def test_update(temp_manuscript):
    old_author = ms.read_one(temp_manuscript)[ms.AUTHOR]
    old_author_email = ms.read_one(temp_manuscript)[ms.AUTHOR_EMAIL]
    old_text = ms.read_one(temp_manuscript)[ms.TEXT]
    old_abstract = ms.read_one(temp_manuscript)[ms.ABSTRACT]
    old_editor_email = ms.read_one(temp_manuscript)[ms.EDITOR_EMAIL]
    title = ms.update(temp_manuscript, TEST_AUTHOR, TEST_AUTHOR_EMAIL, 
                      TEST_TEXT, TEST_ABSTRACT, TEST_EDITOR_EMAIL)
    updated_author = ms.read_one(temp_manuscript)[ms.AUTHOR]
    updated_author_email = ms.read_one(temp_manuscript)[ms.AUTHOR_EMAIL]
    updated_text = ms.read_one(temp_manuscript)[ms.TEXT]
    updated_abstract = ms.read_one(temp_manuscript)[ms.ABSTRACT]
    updated_editor_email = ms.read_one(temp_manuscript)[ms.EDITOR_EMAIL]
    assert title == temp_manuscript
    assert old_author != updated_author
    assert old_author_email != updated_author_email
    assert old_text != updated_text
    assert old_abstract != updated_abstract
    assert old_editor_email != updated_editor_email
    assert updated_author == TEST_AUTHOR
    assert updated_author_email == TEST_AUTHOR_EMAIL
    assert updated_text == TEST_TEXT
    assert updated_abstract == TEST_ABSTRACT
    assert updated_editor_email == TEST_EDITOR_EMAIL
