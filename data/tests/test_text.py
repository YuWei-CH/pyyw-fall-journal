import pytest
import data.text as txt

TEMP_PAGE = '1'
TEMP_TITLE = 'Temp Text Title'
TEMP_TEXT = 'Test Text Content'
TEMP_MANUSCRIPT = 'test_manuscript_id'

TEST_PAGE = '2'
TEST_TITLE = 'Updated Text Title'
TEST_TEXT = "Test Text"
TEST_MANUSCRIPT = 'test_manuscript_id2'


@pytest.fixture(scope='function')
def temp_text():
    page_number = txt.create(TEST_MANUSCRIPT, TEMP_PAGE, TEMP_TITLE, TEMP_TEXT)
    yield page_number
    try:
        txt.delete(page_number)
    except:
        print('Page already deleted. ')


def test_exists(temp_text):
    assert txt.exists(temp_text, TEST_MANUSCRIPT)


def test_doesnt_exist():
    assert not txt.exists('Not an existing page number!')


def test_create():
    assert not txt.exists(TEST_PAGE, TEST_MANUSCRIPT)
    txt.create(TEST_MANUSCRIPT, TEST_PAGE, TEST_TITLE, TEST_TEXT)
    assert txt.exists(TEST_PAGE, TEST_MANUSCRIPT)
    txt.delete(TEST_PAGE)


def test_create_blank_page_number():
    with pytest.raises(ValueError):
        txt.create(TEST_MANUSCRIPT, " ", "Not Care", "Not Care")


def test_create_blank_title():
    with pytest.raises(ValueError):
        txt.create(TEST_MANUSCRIPT, "Not Care", " ", "Not Care")


def test_create_blank_text():
    with pytest.raises(ValueError):
        txt.create(TEST_MANUSCRIPT, "Not Care", "Not Care", " ")


def test_create_duplicate(temp_text):
    with pytest.raises(ValueError):
        txt.create(TEST_MANUSCRIPT, temp_text, TEMP_TITLE, TEMP_TEXT)


def test_read(temp_text):
    texts = txt.read()
    assert isinstance(texts, dict)
    assert len(texts) > 0
    for page_number, text in texts.items():
        assert isinstance(page_number, str)
        assert txt.PAGE_NUMBER in text
        assert txt.TITLE in text
        assert txt.TEXT in text


def test_read_one(temp_text):
    assert txt.read_one(temp_text, TEST_MANUSCRIPT) is not None


def test_read_one_not_there():
    assert txt.read_one('Not an existing page number!') is None


def test_delete(temp_text):
    txt.delete(temp_text)
    assert not txt.exists(temp_text, TEST_MANUSCRIPT)


def test_delete_not_found():
    result = txt.delete('Not an existing page number!')
    assert result is None


def test_update(temp_text):
    old_title = txt.read_one(temp_text, TEST_MANUSCRIPT)[txt.TITLE]
    old_text = txt.read_one(temp_text, TEST_MANUSCRIPT)[txt.TEXT]
    page_number = txt.update(TEST_MANUSCRIPT, temp_text, TEST_TITLE, TEST_TEXT)
    updated_title = txt.read_one(temp_text, TEST_MANUSCRIPT)[txt.TITLE]
    updated_text = txt.read_one(temp_text, TEST_MANUSCRIPT)[txt.TEXT]
    assert page_number == temp_text
    assert old_title != updated_title
    assert old_text != updated_text
    assert updated_title == TEST_TITLE
    assert updated_text == TEST_TEXT


def test_update_invalid_page_number():
    with pytest.raises(ValueError):
        txt.update(TEST_MANUSCRIPT, 'Wrong Page', "Not Care", "Not Care")


def test_update_blank_title(temp_text):
    with pytest.raises(ValueError):
        txt.update(TEST_MANUSCRIPT, temp_text, " ", "Not Care")


def test_update_blank_text(temp_text):
    with pytest.raises(ValueError):
        txt.update(TEST_MANUSCRIPT, temp_text, "Not Care", " ")
