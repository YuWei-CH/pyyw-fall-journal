import pytest

import data.people as ppl
from data.roles import TEST_CODE


COMPLETE = "football@nba.edu"
NO_NAME = '@nba.edu'
NO_AT = 'football'
NO_DOMAIN = 'football@'
SPEC_CHAR = "wayne#e@nba.edu"
UND_SCR = "wayne_ll@nba.edu"
DOT = "wayne.ll@nba.edu"
DASH = "wayne-ll@nba.edu"
DASH_DOMAIN = "wayne@nba-nfl.edu"
DOT_START = ".wayne@nba.edu"
DASH_END = "wayne-@nba.edu"
CONSECUTIVE_DOTS = "wayne..ll@nba.edu"
DOMAIN_DOMAIN_MISSING = "wayne@nba"
DOMAIN_SPEC_CHR = "wayne@nba!#!?nfl.edu"
DOMAIN_CONSEC_DOTS = "wayne@nba..edu"
DOMAIN_START_DOTS = "wayne@.nba.edu"
DOMAIN_2_CHR_LESS = "wayne@nba.e"
DOMAIN_2_CHR_MORE = "wayne@nba.edsd"

TEMP_EMAIL = 'temp_person@temp.org'


@pytest.fixture(scope='function')
def temp_person():
    _id = ppl.create('Peter Peter', 'PKU', TEMP_EMAIL, TEST_CODE)
    yield _id
    ppl.delete(_id)


def test_is_mail_valid_full():
    assert ppl.is_valid_email(COMPLETE)


def test_is_mail_valid_atless():
    assert not ppl.is_valid_email(NO_AT)


def test_is_mail_valid_nameless():
    assert not ppl.is_valid_email(NO_NAME)


def test_is_mail_valid_domainless():
    assert not ppl.is_valid_email(NO_DOMAIN)


def test_has_special_chars():
    assert not ppl.is_valid_email(SPEC_CHAR)


def test_has_underscore():
    assert ppl.is_valid_email(UND_SCR)


def test_has_dot():
    assert ppl.is_valid_email(DOT)


def test_has_dash():
    assert ppl.is_valid_email(DASH)


def test_domain_with_dash():
    assert ppl.is_valid_email(DASH_DOMAIN)


def test_start_with_dot():
    assert not ppl.is_valid_email(DOT_START)


def test_consecutive_dots():
    assert not ppl.is_valid_email(CONSECUTIVE_DOTS)


def test_domain_missing_last():
    assert not ppl.is_valid_email(DOMAIN_DOMAIN_MISSING)


def test_domain_special_char():
    assert not ppl.is_valid_email(DOMAIN_SPEC_CHR)


def test_domain_consecutive_dot():
    assert not ppl.is_valid_email(DOMAIN_CONSEC_DOTS)


def test_domain_start_with_dot():
    assert not ppl.is_valid_email(DOMAIN_START_DOTS)


def test_domain_less_than_two_char():
    assert not ppl.is_valid_email(DOMAIN_2_CHR_LESS)


def test_domain_more_than_two_char():
    assert ppl.is_valid_email(DOMAIN_2_CHR_MORE)


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


VALID_ROLES = ['ED', 'AU']


@pytest.mark.skip('Skipping cause the update method for people is not done to take in roles.')
def test_update(temp_person):
    ppl.update('Buffalo Bill', 'UBuffalo', temp_person, VALID_ROLES)
