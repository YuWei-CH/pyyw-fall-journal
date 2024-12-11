import pytest
import data.text as txt

Test_KEY = "TestPage"


@pytest.fixture(scope='function')
def temp_text():
    page_number = txt.create("TestPage", "Test Title", "Test Text")
    yield page_number
    try:
        txt.delete(page_number)
    except:
        print('Page already deleted. ')


def test_create(temp_text):
    text = txt.read()
    assert Test_KEY in text


def test_create_blank():
    with pytest.raises(ValueError):
        txt.create("Not Care", " ", " ")


def test_create_duplicate(temp_text):
    with pytest.raises(ValueError):
        txt.create(temp_text, "Not Care", "Not Care")


def test_read(temp_text):
    texts = txt.read()
    assert isinstance(texts, dict)
    assert len(texts) > 0
    for page_number, text in texts.items():
        assert isinstance(page_number, str)
        assert txt.TITLE in text
        assert txt.TEXT in text


def test_read_one(temp_text):
    assert len(txt.read_one(temp_text)) > 0


def test_read_one_not_found():
    assert txt.read_one('Not a page number!') != {}


def test_delete(temp_text):
    texts = txt.read()
    old_len = len(texts)
    txt.delete(temp_text)
    texts = txt.read()
    assert len(texts) < old_len
    assert temp_text not in texts


def test_delete_not_found():
    result = txt.delete('Not a page key!')
    assert result is None


NEW_TITLE = "New Test Title"
NEW_TEXT = "New Test Text"


def test_update_title(temp_text):
    text = txt.read()
    old_title = text[temp_text][txt.TITLE]
    updated_page_number = txt.update(temp_text, txt.TITLE, NEW_TITLE)
    text = txt.read()
    new_title = text[temp_text][txt.TITLE]
    assert old_title != new_title
    assert new_title == NEW_TITLE
    assert updated_page_number == temp_text


def test_update_text(temp_text):
    text = txt.read()
    old_text = text[temp_text][txt.TEXT]
    updated_page_number = txt.update(temp_text, txt.TEXT, NEW_TEXT)
    text = txt.read()
    new_text = text[temp_text][txt.TEXT]
    assert old_text != new_text
    assert new_text == NEW_TEXT
    assert updated_page_number == temp_text


def test_update_false_page_number():
    with pytest.raises(ValueError):
        txt.update('Wrong Page', txt.TITLE, "Not Care")


def test_update_invalid_field(temp_text):
    with pytest.raises(ValueError):
        txt.update(temp_text, "Invalid Field", "Not Care")


def test_update_empty_value(temp_text):
    with pytest.raises(ValueError):
        txt.update(temp_text, txt.TITLE, " ")
