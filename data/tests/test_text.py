import pytest
import data.text as txt
from data.text import TITLE, TEXT 

def test_create():
    text = txt.read()
    assert Contact_KEY not in text
    txt.create(Contact_KEY, 'Contact Us', 'This is a Contact page.')
    people = txt.read()
    assert Contact_KEY in people


def test_read():
    texts = txt.read()
    assert isinstance(texts, dict)
    for page_number in texts:
        assert isinstance(page_number, str)

@pytest.fixture(scope='function')
def temp_text():
    _page_number = txt.create("TestPage", "Test Title", "Test Text")
    yield _page_number
    txt.delete(_page_number)

def test_read_one(temp_text):
    assert len(txt.read_one(temp_text)) > 0


def test_read_one_not_found():
    assert txt.read_one('Not a page number!') == {}


def test_delete():
    texts = txt.read()
    old_len = len(texts)
    txt.delete(txt.DEL_PAGE_NUMBER)
    texts = txt.read()
    assert len(texts) < old_len
    assert txt.DEL_PAGE_NUMBER not in texts


def test_delete_not_found():
    result = txt.delete('Not a page key!')
    assert result is None


Contact_KEY = 'ContactUs'

def test_create_duplicate():
    with pytest.raises(ValueError):
        txt.create(txt.TEST_PAGE_NUMBER,
                          "Not care", "Nothing")


NEW_TITLE = "New Test Title"
NEW_TEXT = "New Test Text"


def test_update_title():
    text = txt.read()
    old_title = text[txt.TEST_PAGE_NUMBER][txt.TITLE]
    updated_page_number = txt.update(txt.TEST_PAGE_NUMBER, txt.TITLE, NEW_TITLE)
    text = txt.read()
    new_title = text[txt.TEST_PAGE_NUMBER][txt.TITLE]
    assert old_title != new_title
    assert new_title == NEW_TITLE
    assert updated_page_number == txt.TEST_PAGE_NUMBER


def test_update_text():
    text = txt.read()
    old_text = text[txt.TEST_PAGE_NUMBER][txt.TEXT]
    updated_page_number = txt.update(txt.TEST_PAGE_NUMBER, txt.TEXT, NEW_TEXT)
    text = txt.read()
    new_text = text[txt.TEST_PAGE_NUMBER][txt.TEXT]
    assert old_text != new_text
    assert new_text == NEW_TEXT
    assert updated_page_number == txt.TEST_PAGE_NUMBER


FALSE_PAGE_NUMBER = 'wrong page'
def test_update_false_page_number():
    with pytest.raises(ValueError):
        txt.update(FALSE_PAGE_NUMBER, txt.TITLE, "Not Care")
