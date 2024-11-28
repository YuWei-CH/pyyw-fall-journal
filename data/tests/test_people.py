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
    try:
        ppl.delete(_id)
    except:
        print('Person already deleted.')


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


def test_read(temp_person):
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
UPDATE_ROLE_CODE = "CH"


def test_get_masthead():
    mh = ppl.get_masthead()
    assert isinstance(mh, dict)


def test_create():
    people = ppl.read()
    assert ADD_EMAIL not in people
    ppl.create('Joe Smith', 'NYU', ADD_EMAIL, TEST_CODE)
    assert ppl.exists(ADD_EMAIL)
    ppl.delete(ADD_EMAIL)


def test_create_duplicate(temp_person):
    with pytest.raises(ValueError):
        ppl.create('Do not care about name', 
                    'Or affiliation', temp_person, 
                    TEST_CODE)


def test_exists(temp_person):
    assert ppl.exists(temp_person)


def test_doesnt_exist():
    assert not ppl.exists('Not an existing email!')


def test_delete(temp_person):
    ppl.delete(temp_person)
    assert not ppl.exists(temp_person)


def test_update_blank_value():
    with pytest.raises(ValueError):
        ppl.update(ppl.TEST_EMAIL, ppl.NAME, " ")


def test_update_invalid_email():
    result = ppl.update("wrong email", ppl.NAME, "Not Care")
    assert result is None


def test_update_invalid_field():
    with pytest.raises(ValueError):
        ppl.update(ppl.TEST_EMAIL, "invalid field", "Not Care")


def test_update_name():
    people = ppl.read()
    old_name = people[ppl.TEST_EMAIL][ppl.NAME]
    updated_email = ppl.update(ppl.TEST_EMAIL, ppl.NAME, UPDATE_NAME)
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
    updated_email = ppl.update(ppl.TEST_EMAIL, ppl.AFFILIATION, UPDATE_AFFILIATION)
    people = ppl.read()
    new_affiliation = people[ppl.TEST_EMAIL][ppl.AFFILIATION]
    assert updated_email == ppl.TEST_EMAIL
    assert new_affiliation == UPDATE_AFFILIATION
    assert old_affiliation != new_affiliation


def test_add_role():
    """
    Test the add_role() function
    """
    people = ppl.read()
    old_roles = people[ppl.TEST_EMAIL][ppl.ROLES]
    assert UPDATE_ROLE_CODE not in old_roles
    _id = ppl.add_role(ppl.TEST_EMAIL, UPDATE_ROLE_CODE)
    assert _id != None
    people = ppl.read()
    new_roles = people[ppl.TEST_EMAIL][ppl.ROLES]
    assert UPDATE_ROLE_CODE in new_roles


def test_add_blank_role():
    """
    Test the add_role() function with blank role
    """
    people = ppl.read()
    old_roles = people[ppl.TEST_EMAIL][ppl.ROLES]
    assert UPDATE_ROLE_CODE in old_roles
    with pytest.raises(ValueError):
        _id = ppl.add_role(ppl.TEST_EMAIL, "")
        assert _id == None


def test_add_duplicate_role():
    """
    Test the add_role() function with duplicate role
    """
    people = ppl.read()
    old_roles = people[ppl.TEST_EMAIL][ppl.ROLES]
    assert UPDATE_ROLE_CODE in old_roles
    with pytest.raises(ValueError):
        _id = ppl.add_role(ppl.TEST_EMAIL, UPDATE_ROLE_CODE)
        assert _id == None


def test_delete_role():
    """
    Test the delete_role() function
    """
    # Now delete the role
    _id = ppl.delete_role(ppl.TEST_EMAIL, UPDATE_ROLE_CODE)
    assert _id is not None
    people = ppl.read()
    new_roles = people[ppl.TEST_EMAIL][ppl.ROLES]
    assert UPDATE_ROLE_CODE not in new_roles


def test_delete_blank_role():
    """
    Test the delete_role() function with a blank role
    """
    with pytest.raises(ValueError):
        _id = ppl.delete_role(ppl.TEST_EMAIL, "")
        assert _id is None


def test_delete_nonexistent_role():
    """
    Test the delete_role() function with a role that doesn't exist
    """
    people = ppl.read()
    old_roles = people[ppl.TEST_EMAIL][ppl.ROLES]
    assert UPDATE_ROLE_CODE not in old_roles
    with pytest.raises(ValueError):
        _id = ppl.delete_role(ppl.TEST_EMAIL, UPDATE_ROLE_CODE)
        assert _id is None


def test_delete_role_nonexistent_user():
    """
    Test deleting a role from a non-existent user
    """
    nonexistent_email = 'nonexistent@domain.com'
    with pytest.raises(ValueError):
        _id = ppl.delete_role(nonexistent_email, UPDATE_ROLE_CODE)
        assert _id is None
