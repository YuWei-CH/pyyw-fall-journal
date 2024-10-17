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
UPDATE_AFFILIATION = "MIT"


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
    updated_email = ppl.update_name(ppl.TEST_EMAIL, UPDATE_NAME)
    people = ppl.read()
    new_name = people[ppl.TEST_EMAIL][ppl.NAME]
    assert old_name != new_name
    assert new_name == UPDATE_NAME
    assert updated_email == ppl.TEST_EMAIL


def test_update_affiliation():
    """
    Test the update_affiliation() function to ensure a user's affiliation is updated successfully.
    """
    people = ppl.read()
    old_affiliation = people[ppl.TEST_EMAIL][ppl.AFFILIATION]
    updated_email = ppl.update_affiliation(ppl.TEST_EMAIL, UPDATE_AFFILIATION)
    people = ppl.read()
    new_affiliation = people[ppl.TEST_EMAIL][ppl.AFFILIATION]
    assert updated_email == ppl.TEST_EMAIL
    assert new_affiliation == UPDATE_AFFILIATION
    assert old_affiliation != new_affiliation


def test_update_affiliation_blank():
    """
    Test the update_affiliation() function to ensure it raises a ValueError when the new affiliation is blank.
    """
    with pytest.raises(ValueError):
        ppl.update_affiliation(ppl.TEST_EMAIL, " ")

