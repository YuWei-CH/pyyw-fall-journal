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

new_title = "New Test Title"
new_text = "New Test Text"

def test_update(temp_text):
    text = txt.read()
    assert temp_text in text
    old_entry = txt.read_one(temp_text)
    assert old_entry[TITLE] != new_title
    assert old_entry[TEXT] != new_text
    txt.update(temp_text, new_title, new_text)
    updated_entry = txt.read_one(temp_text)
    assert updated_entry[TITLE] == new_title
    assert updated_entry[TEXT] == new_text

FALSE_PAGE_NUMBER = 'wrong page'
def test_update_false():
    with pytest.raises(ValueError):
        txt.update(FALSE_PAGE_NUMBER, new_title, new_text)

@pytest.mark.skip('Skipping cause test_update_text_only not done.')
def test_update_text_only(temp_text):
    txt.update_text(temp_text, 'Updated Text')

