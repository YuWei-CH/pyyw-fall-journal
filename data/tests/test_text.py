import data.text as txt

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
