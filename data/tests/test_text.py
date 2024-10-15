import pytest

import data.text as txt

def test_read():
    text = txt.read()
    assert isinstance((text), dict)
    assert len(text) > 0
    # check for string IDs:
    for _key, content in text.items():
        assert isinstance(_key, str)
        assert txt.KEY in content
        

