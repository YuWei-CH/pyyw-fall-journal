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


def test_read_one(temp_person):
    assert ppl.read_one(temp_person) is not None


def test_read_one_not_there():
    assert ppl.read_one('Not an existing email!') is None


def test_get_mh_fields():
    flds = ppl.get_mh_fields()
    assert isinstance(flds, list)
    assert len(flds) > 0


def test_create_mh_rec(temp_person):
    person_rec = ppl.read_one(temp_person)
    mh_rec = ppl.create_mh_rec(person_rec)
    assert isinstance(mh_rec, dict)
    for field in ppl.MH_FIELDS:
        assert field in mh_rec


def test_get_masthead():
    mh = ppl.get_masthead()
    assert isinstance(mh, dict)


def test_has_role(temp_person):
    person_rec = ppl.read_one(temp_person)
    assert ppl.has_role(person_rec, TEST_CODE)


def test_doesnt_have_role(temp_person):
    person_rec = ppl.read_one(temp_person)
    assert not ppl.has_role(person_rec, 'Not a good role!')


ADD_EMAIL = 'joe@nyu.edu'
UPDATE_NAME = 'Yuwei Sun'
UPDATE_AFFILIATION = "MIT"
UPDATE_ROLE_CODE = "CE"


def test_create():
    assert not ppl.exists(ADD_EMAIL)
    ppl.create('Joe Smith', 'NYU', ADD_EMAIL, TEST_CODE)
    assert ppl.exists(ADD_EMAIL)
    ppl.delete(ADD_EMAIL)


def test_create_duplicate(temp_person):
    with pytest.raises(ValueError):
        ppl.create('Do not care about name', 
                    'Or affiliation', temp_person, 
                    TEST_CODE)


def test_create_bad_email():
    with pytest.raises(ValueError):
        ppl.create('Do not care about name', 
                   'Or affiliation', 'bademail', TEST_CODE)


def test_create_invalid_role():
    with pytest.raises(ValueError):
        ppl.create('Do not care about name', 
                   'Or affiliation', 'goodemail@gmail.com', 'badrole')


def test_create_empty_name():
    with pytest.raises(ValueError):
        ppl.create(' ', ' ', 'goodemail@gmail.com', TEST_CODE)


def test_exists(temp_person):
    assert ppl.exists(temp_person)


def test_doesnt_exist():
    assert not ppl.exists('Not an existing email!')


def test_delete(temp_person):
    ppl.delete(temp_person)
    assert not ppl.exists(temp_person)


def test_update_blank_value(temp_person):
    with pytest.raises(ValueError):
        ppl.update(temp_person, " ", " ")


def test_update_invalid_email():
    with pytest.raises(ValueError):
        ppl.update("wrong email", "Not Care", "Not Care")


def test_update(temp_person):
    old_name = ppl.read_one(temp_person)[ppl.NAME]
    old_affiliation = ppl.read_one(temp_person)[ppl.AFFILIATION]
    email = ppl.update(temp_person, UPDATE_NAME, UPDATE_AFFILIATION)
    new_name = ppl.read_one(temp_person)[ppl.NAME]
    new_affiliation = ppl.read_one(temp_person)[ppl.AFFILIATION]
    assert old_name != new_name
    assert old_affiliation != new_affiliation
    assert new_name == UPDATE_NAME
    assert new_affiliation == UPDATE_AFFILIATION
    assert email == temp_person


def test_add_role(temp_person):
    old_roles = ppl.read_one(temp_person)[ppl.ROLES]
    assert UPDATE_ROLE_CODE not in old_roles
    email = ppl.add_role(temp_person, UPDATE_ROLE_CODE)
    assert email == temp_person
    new_roles = ppl.read_one(temp_person)[ppl.ROLES]
    assert UPDATE_ROLE_CODE in new_roles


def test_add_duplicate_role(temp_person):
    roles = ppl.read_one(temp_person)[ppl.ROLES]
    assert TEST_CODE in roles
    with pytest.raises(ValueError):
        ppl.add_role(temp_person, TEST_CODE)


def test_add_invalid_role(temp_person):
    with pytest.raises(ValueError):
        ppl.add_role(temp_person, "invalid role")


def test_add_role_invalid_email():
    with pytest.raises(ValueError):
        ppl.add_role("invalid email", UPDATE_ROLE_CODE)


def test_delete_role(temp_person):
    old_roles = ppl.read_one(temp_person)[ppl.ROLES]
    assert TEST_CODE in old_roles
    email = ppl.delete_role(temp_person, TEST_CODE)
    assert email == temp_person
    new_roles = ppl.read_one(temp_person)[ppl.ROLES]
    assert TEST_CODE not in new_roles


def test_delete_not_existing_role(temp_person):
    roles = ppl.read_one(temp_person)[ppl.ROLES]
    assert UPDATE_ROLE_CODE not in roles
    with pytest.raises(ValueError):
        ppl.delete_role(temp_person, UPDATE_ROLE_CODE)


def test_delete_role_invalid_email():
    with pytest.raises(ValueError):
        ppl.delete_role("invalid email", UPDATE_ROLE_CODE)
