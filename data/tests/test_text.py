import pytest
import data.text as txt
from data.text import TEST_KEY, TITLE, TEXT

def test_read():
    texts = txt.read()
    assert isinstance(texts, dict)
    for key in texts:
        assert isinstance(key, str)


def test_read_one():
    assert len(txt.read_one(txt.TEST_KEY)) > 0


def test_read_one_not_found():
    assert txt.read_one('Not a page key!') == {}


def test_delete():
    texts = txt.read()
    old_len = len(texts)
    txt.delete(txt.DEL_KEY)
    texts = txt.read()
    assert len(texts) < old_len
    assert txt.DEL_KEY not in texts


def test_delete_not_found():
    result = txt.delete('Not a page key!')
    assert result is None


Contact_KEY = 'ContactUs'


def test_create():
    text = txt.read()
    assert Contact_KEY not in text
    txt.create(Contact_KEY, 'Contact Us', 'This is a Contact page.')
    people = txt.read()
    assert Contact_KEY in people


def test_create_duplicate():
    with pytest.raises(ValueError):
        txt.create(txt.TEST_KEY,
                          "Not care", "Nothing")


new_title = 'NBA Front Page'
new_text = 'new season coming up. Go Phoenix!'


def test_update():
    text = txt.read()
    assert TEST_KEY in text
    old_title = text[TEST_KEY][TITLE]
    old_text = text[TEST_KEY][TEXT]
    assert old_title != new_title
    assert old_text != new_text
    txt.update(TEST_KEY, new_title, new_text)


FALSE_KEY = 'wrong page'
def test_update_false():
    with pytest.raises(ValueError):
        txt.update(FALSE_KEY, new_title, new_text)

