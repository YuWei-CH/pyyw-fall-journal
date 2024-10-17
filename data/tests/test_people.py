import pytest

import data.people as ppl

def test_read():
    people = ppl.read()
    assert isinstance(people, dict)
    assert len(people) > 0
    # check for string IDs:
    for _id, person in people.items():
        assert isinstance(_id, str)
        assert ppl.NAME in person



ADD_EMAIL = 'joe@nyu.edu'
UPDATE_NAME = 'Yuwei Sun'


def test_create():
    people = ppl.read()
    assert ADD_EMAIL not in people
    ppl.create('Joe Smith', 'NYU', ADD_EMAIL)
    people = ppl.read()
    assert ADD_EMAIL in people


def test_create_duplicate():
    with pytest.raises(ValueError):
        ppl.create('Do not care about name',
                          'Or affiliation', ppl.TEST_EMAIL)


def test_delete():
    people = ppl.read()
    old_len = len(people)
    ppl.delete(ppl.DEL_EMAIL)
    people = ppl.read()
    assert len(people) < old_len
    assert ppl.DEL_EMAIL not in people


def test_update_name_blank():
    with pytest.raises(ValueError):
        ppl.update_name(ppl.TEST_EMAIL, " ")


def test_update_name():
    people = ppl.read()
    old_name = people[ppl.TEST_EMAIL][ppl.NAME]
    ppl.update_name(ppl.TEST_EMAIL, UPDATE_NAME)
    people = ppl.read()
    new_name = people[ppl.TEST_EMAIL][ppl.NAME]
    assert old_name != new_name
    assert new_name == UPDATE_NAME
