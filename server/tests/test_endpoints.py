from http import HTTPStatus
from http.client import (
    BAD_REQUEST,
    FORBIDDEN,
    NOT_ACCEPTABLE,
    NOT_FOUND,
    OK,
    SERVICE_UNAVAILABLE,
)

from unittest.mock import patch

import pytest, json

from data.people import ID, NAME, AFFILIATION, EMAIL, ROLES, BIO
import server.endpoints as ep

TEST_CLIENT = ep.app.test_client()

import data.text as txt
import data.roles as rls
from data.text import *
import data.manuscript as ms
import data.comment as cmt

from unittest.mock import patch
from datetime import datetime
import platform

TEST_MANU_ID = "test_manu_id"
TEST_EMAIL = "testEmail@gmail.com"
TEST_TITLE = "Test Manuscript Title"
TEST_PAGE_NUMBER = "TestPageNumber"
TEST_CLIENT = ep.app.test_client()
GOOD_USER_RECORD = {'email': TEST_EMAIL, 'roles': ['ME', 'RE', 'ED']}
AUTH_HEADERS = {'X-User-Id': GOOD_USER_RECORD['email']}

ADD_DELETE_ROLE_DATA = {
    ID: TEST_MANU_ID,
    ep.ROLE: rls.TEST_CODE
}

def test_hello():
    resp = TEST_CLIENT.get(ep.HELLO_EP)
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert ep.HELLO_RESP in resp_json


def test_title():
    resp = TEST_CLIENT.get(ep.TITLE_EP)
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert ep.TITLE_RESP in resp_json
    assert isinstance(resp_json[ep.TITLE_RESP], str)
    assert len(resp_json[ep.TITLE_RESP]) > 0


@patch('data.roles.read', autospec=True,
        return_value={'ED': 'Editor'})
def test_read_roles(mock_read):
    resp = TEST_CLIENT.get(ep.ROLES_EP)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    for role_code, role_name in resp_json.items():
        assert isinstance(role_code, str)
        assert isinstance(role_name, str)
        assert len(role_code) > 0
        assert len(role_name) > 0


@patch('data.people.read', autospec=True,
        return_value={'id': {NAME: 'Joe Schmoe'}})
def test_read_people(mock_read):
    resp = TEST_CLIENT.get(ep.PEOPLE_EP)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    for _id, person in resp_json.items():
        assert isinstance(_id, str)
        assert len(_id) > 0
        assert NAME in person


@patch('data.people.get_all_people', autospec=True,
        return_value=["Name (email)"])
def test_get_all_people(mock_get_all_people):
    resp = TEST_CLIENT.get(f'{ep.PEOPLE_EP}/get_all_people')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, list)
    for item in resp_json:
        assert isinstance(item, str)


@patch('data.people.read_one', autospec=True,
       return_value={NAME: 'Joe Schmoe'})
def test_read_one_person(mock_read):
    resp = TEST_CLIENT.get(f'{ep.PEOPLE_EP}/mock_id')
    assert resp.status_code == OK


@patch('data.people.read_one', autospec=True, return_value=None)
def test_read_one_person_not_found(mock_read):
    resp = TEST_CLIENT.get(f'{ep.PEOPLE_EP}/mock_id')
    assert resp.status_code == NOT_FOUND


@patch('data.people.read_one', return_value=GOOD_USER_RECORD)
@patch('data.people.delete', return_value='test@example.com')
def test_delete_people(mock_delete, mock_read_one):
    resp = TEST_CLIENT.delete(
        f'{ep.PEOPLE_EP}/mock_email?email=yw5490@nyu.edu',
        headers=AUTH_HEADERS
    )
    assert resp.status_code == HTTPStatus.OK


@patch('data.people.read_one', return_value=GOOD_USER_RECORD)
@patch('data.people.delete', return_value=None)
def test_delete_people_not_found(mock_delete, mock_read_one):
    resp = TEST_CLIENT.delete(
        f'{ep.PEOPLE_EP}/mock_email?email=yw5490@nyu.edu',
        headers=AUTH_HEADERS
    )
    assert resp.status_code == HTTPStatus.NOT_FOUND


CREATE_TEST_DATA = {
    NAME: "Test Name",
    AFFILIATION: "Test Affiliation",
    EMAIL: TEST_EMAIL,
    ROLES: rls.TEST_CODE
}

# ensure read() comes back empty so the "first user" branch skips ED/ME check
@patch('data.people.read', autospec=True, return_value=[])
@patch('data.people.create', autospec=True, return_value=TEST_EMAIL)
def test_create_people(mock_create, mock_read):
    resp = TEST_CLIENT.post(
        f'{ep.PEOPLE_EP}/create',
        data=json.dumps(CREATE_TEST_DATA),
        content_type='application/json'
    )
    assert resp.status_code == HTTPStatus.CREATED


@patch('data.people.read', autospec=True, return_value=[])
@patch('data.people.create', autospec=True, side_effect=ValueError("Mocked Exception"))
def test_create_people_failed(mock_create, mock_read):
    resp = TEST_CLIENT.post(
        f'{ep.PEOPLE_EP}/create',
        data=json.dumps(CREATE_TEST_DATA),
        content_type='application/json'
    )
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR 


UPDATE_PEOPLE_DATA = {
    EMAIL: TEST_EMAIL,
    NAME: "Yirong Wang",
    AFFILIATION: "NYU",
}


@patch('data.people.read_one', return_value=GOOD_USER_RECORD)
@patch('data.people.update', autospec=True, return_value=TEST_EMAIL)
def test_update_people(mock_update, mock_read_one):
    resp = TEST_CLIENT.put(
        f'{ep.PEOPLE_EP}/update',
        data=json.dumps(UPDATE_PEOPLE_DATA),
        content_type='application/json',
        headers=AUTH_HEADERS
    )
    assert resp.status_code == OK
    assert resp.get_json() == TEST_EMAIL


@patch('data.people.read_one', return_value=GOOD_USER_RECORD)
@patch('data.people.update', autospec=True, side_effect=ValueError("Mocked Exception"))
def test_update_people_failed(mock_update, mock_read_one):
    resp = TEST_CLIENT.put(
        f'{ep.PEOPLE_EP}/update',
        data=json.dumps(UPDATE_PEOPLE_DATA),
        content_type='application/json',
        headers=AUTH_HEADERS
    )
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR


@patch("data.people.read_one", autospec=True, return_value={"id": TEST_MANU_ID, "roles": ["ME"]})
@patch("data.people.add_role", autospec=True, return_value=TEST_MANU_ID)
def test_add_role_success(mock_add, mock_read_one):
    """PUT /people/add_role → 200 + {message, return} when add_role succeeds"""
    resp = TEST_CLIENT.put(
        f"{ep.PEOPLE_EP}/add_role",
        headers=AUTH_HEADERS,
        data=json.dumps(ADD_DELETE_ROLE_DATA),
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.OK
    body = resp.get_json()
    assert ep.MESSAGE in body and ep.RETURN in body
    assert TEST_MANU_ID in body[ep.MESSAGE]
    assert body[ep.RETURN] == TEST_MANU_ID
    mock_add.assert_called_once_with(TEST_MANU_ID, rls.TEST_CODE)
    

@patch("data.people.read_one", autospec=True, return_value={"id": TEST_MANU_ID, "roles": ["ME"]})
@patch("data.people.add_role", autospec=True, side_effect=ValueError("mock failure"))
def test_add_role_failure(mock_add, mock_read_one):
    """PUT /people/add_role → 406 when add_role() raises"""
    resp = TEST_CLIENT.put(
        f"{ep.PEOPLE_EP}/add_role",
        headers=AUTH_HEADERS,
        data=json.dumps(ADD_DELETE_ROLE_DATA),
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.NOT_ACCEPTABLE


@patch("data.people.read_one", autospec=True, return_value={"id": TEST_MANU_ID, "roles": ["ED"]})
@patch("data.people.delete_role", autospec=True, return_value=TEST_MANU_ID)
def test_delete_role_success(mock_delete, mock_read_one):
    """DELETE /people/delete_role → 200 + {message, return} when delete_role succeeds"""
    resp = TEST_CLIENT.delete(
        f"{ep.PEOPLE_EP}/delete_role",
        headers=AUTH_HEADERS,
        data=json.dumps(ADD_DELETE_ROLE_DATA),
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.OK
    body = resp.get_json()
    assert ep.MESSAGE in body and ep.RETURN in body
    assert TEST_MANU_ID in body[ep.MESSAGE]
    assert body[ep.RETURN] == TEST_MANU_ID
    mock_delete.assert_called_once_with(TEST_MANU_ID, rls.TEST_CODE)


@patch("data.people.read_one", autospec=True, return_value={"id": TEST_MANU_ID, "roles": ["ED"]})
@patch("data.people.delete_role", autospec=True, side_effect=ValueError("mock failure"))
def test_delete_role_failure(mock_delete, mock_read_one):
    """DELETE /people/delete_role → 406 when delete_role() raises"""
    resp = TEST_CLIENT.delete(
        f"{ep.PEOPLE_EP}/delete_role",
        headers=AUTH_HEADERS,
        data=json.dumps(ADD_DELETE_ROLE_DATA),
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.NOT_ACCEPTABLE


@patch('data.text.read', autospec=True,
       return_value={'page_number': {TITLE: 'Test Title', TEXT: 'Test Text'}})
def test_read_text(mock_read):
    resp = TEST_CLIENT.get(ep.TEXT_EP)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    for page_number, text in resp_json.items():
        assert isinstance(page_number, str)
        assert len(page_number) > 0
        assert TITLE in text
        assert TEXT in text


@patch('data.text.read_one', autospec=True,
       return_value={TITLE: 'Test Title', TEXT: 'Test Text'})
def test_read_one_text(mock_read):
    resp = TEST_CLIENT.get(f'{ep.TEXT_EP}/mock_page_number')
    assert resp.status_code == OK


@patch('data.text.read_one', autospec=True, return_value=None)
def test_read_one_text_not_found(mock_read):
    resp = TEST_CLIENT.get(f'{ep.TEXT_EP}/mock_page_number')
    assert resp.status_code == NOT_FOUND


TEXT_TEST_DATA = {
    PAGE_NUMBER: TEST_PAGE_NUMBER,
    TITLE: "Test Title",
    TEXT: "Test Text",
}


@patch('data.text.create', autospec=True, return_value=TEST_PAGE_NUMBER)
def test_create_text(mock_create):
    resp = TEST_CLIENT.put(
        f'{ep.TEXT_EP}/create',
        data=json.dumps(TEXT_TEST_DATA),
        content_type='application/json'
    )
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert ep.MESSAGE in resp_json
    assert ep.RETURN in resp_json


@patch('data.text.create', autospec=True, side_effect=ValueError("Mocked Exception"))
def test_create_text_failed(mock_create):
    resp = TEST_CLIENT.put(
        f'{ep.TEXT_EP}/create',
        data=json.dumps(TEXT_TEST_DATA),
        content_type='application/json'
    )
    assert resp.status_code == NOT_ACCEPTABLE


@patch('data.text.delete', autospec=True, return_value=TEST_PAGE_NUMBER)
def test_delete_text(mock_delete):
    resp = TEST_CLIENT.delete(f'{ep.TEXT_EP}/mock_page_number')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert ep.DELETED in resp_json


@patch('data.text.delete', autospec=True, return_value=None)
def test_delete_text_not_found(mock_delete):
    resp = TEST_CLIENT.delete(f'{ep.TEXT_EP}/mock_page_number')
    assert resp.status_code == NOT_FOUND


@patch("data.people.read_one", autospec=True, return_value={"id": TEST_PAGE_NUMBER, "roles": ["ED"]})
@patch('data.text.update', autospec=True, return_value=TEST_PAGE_NUMBER)
def test_update_text(mock_update, mock_read_one):
    resp = TEST_CLIENT.put(
        f'{ep.TEXT_EP}/update',
        headers=AUTH_HEADERS,
        data=json.dumps(TEXT_TEST_DATA),
        content_type='application/json'
    )
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert ep.MESSAGE in resp_json
    assert ep.RETURN in resp_json


@patch("data.people.read_one", autospec=True, return_value={"id": TEST_PAGE_NUMBER, "roles": ["ED"]})
@patch('data.text.update', autospec=True, side_effect=ValueError("Mocked Exception"))
def test_update_text_failed(mock_update, mock_read_one):
    resp = TEST_CLIENT.put(
        f'{ep.TEXT_EP}/update',
        headers=AUTH_HEADERS,
        data=json.dumps(TEXT_TEST_DATA),
        content_type='application/json'
    )
    assert resp.status_code == NOT_ACCEPTABLE


@patch('data.people.get_masthead', autospec=True, return_value={})
def test_get_masthead(mock_get_masthead):
    resp = TEST_CLIENT.get(f'{ep.PEOPLE_EP}/masthead')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert ep.MASTHEAD in resp_json


MANUSCRIPT_DATA = {
    ms.TITLE: "Test Manuscript",
    ms.AUTHOR: "Test Author",
    ms.AUTHOR_EMAIL: TEST_EMAIL, 
    ms.TEXT: "Test Text", 
    ms.ABSTRACT: "Test Abstract", 
    ms.EDITOR_EMAIL: TEST_EMAIL
}


@patch('data.manuscript.read', autospec=True,
       return_value={'title': {ms.TITLE: 'Test Title'}})
def test_read_manuscripts(mock_read):
    resp = TEST_CLIENT.get(ep.MANUSCRIPT_EP)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    for title, manu in resp_json.items():
        assert isinstance(title, str)
        assert len(title) > 0
        assert ms.TITLE in manu


@patch('data.manuscript.read_one', autospec=True,
       return_value={ms.TITLE: 'Test Title'})
def test_read_one_manuscript(mock_read):
    resp = TEST_CLIENT.get(f'{ep.MANUSCRIPT_EP}/mock_manu_id')
    assert resp.status_code == OK


@patch('data.manuscript.read_one', autospec=True, return_value=None)
def test_read_one_manuscript_not_found(mock_read):
    resp = TEST_CLIENT.get(f'{ep.MANUSCRIPT_EP}/mock_manu_id')
    assert resp.status_code == NOT_FOUND


@patch('data.manuscript.delete', autospec=True, return_value=TEST_MANU_ID)
def test_delete_manuscript(mock_delete):
    resp = TEST_CLIENT.delete(f'{ep.MANUSCRIPT_EP}/mock_manu_id')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert ep.DELETED in resp_json


@patch('data.manuscript.delete', autospec=True, return_value=None)
def test_delete_manuscript_not_found(mock_delete):
    resp = TEST_CLIENT.delete(f'{ep.MANUSCRIPT_EP}/mock_manu_id')
    assert resp.status_code == NOT_FOUND


@patch('data.manuscript.create', autospec=True, return_value=TEST_MANU_ID)
def test_create_manuscript(mock_create):
    resp = TEST_CLIENT.put(
        f'{ep.MANUSCRIPT_EP}/create',
        data=json.dumps(MANUSCRIPT_DATA),
        content_type='application/json'
    )
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert ep.MESSAGE in resp_json
    assert ep.RETURN in resp_json


@patch('data.manuscript.create', autospec=True, side_effect=ValueError("Mocked Exception"))
def test_create_manuscript_failed(mock_create):
    resp = TEST_CLIENT.put(
        f'{ep.MANUSCRIPT_EP}/create',
        data=json.dumps(MANUSCRIPT_DATA),
        content_type='application/json'
    )
    assert resp.status_code == NOT_ACCEPTABLE


@patch('data.manuscript.update', autospec=True, return_value=TEST_MANU_ID)
def test_update_manuscript(mock_update):
    resp = TEST_CLIENT.put(
        f'{ep.MANUSCRIPT_EP}/update',
        data=json.dumps(MANUSCRIPT_DATA),
        content_type='application/json'
    )
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert ep.MESSAGE in resp_json
    assert ep.RETURN in resp_json


@patch('data.manuscript.update', autospec=True, side_effect=ValueError("Mocked Exception"))
def test_update_manuscript_failed(mock_update):
    resp = TEST_CLIENT.put(
        f'{ep.MANUSCRIPT_EP}/update',
        data=json.dumps(MANUSCRIPT_DATA),
        content_type='application/json'
    )
    assert resp.status_code == NOT_ACCEPTABLE


STATE_TEST_DATA = {
    ms.MANU_ID: TEST_MANU_ID,
    ep.ACTION: ms.ACCEPT
}


@patch('data.manuscript.update_state', autospec=True, return_value=TEST_MANU_ID)
def test_update_state(mock_update_state):
    resp = TEST_CLIENT.put(
        f'{ep.MANUSCRIPT_EP}/update_state',
        data=json.dumps(STATE_TEST_DATA),
        content_type='application/json'
    )
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert ep.MESSAGE in resp_json
    assert ep.RETURN in resp_json


STATE_TEST_DATA_WITH_REFEREE = {
    ms.MANU_ID: TEST_MANU_ID,
    ep.ACTION: ms.ASSIGN_REF, 
    ep.REFEREE: "Test Referee",
}


@patch('data.manuscript.update_state', autospec=True, return_value=TEST_MANU_ID)
def test_update_state_with_referee(mock_update_state):
    resp = TEST_CLIENT.put(
        f'{ep.MANUSCRIPT_EP}/update_state',
        data=json.dumps(STATE_TEST_DATA_WITH_REFEREE),
        content_type='application/json'
    )
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert ep.MESSAGE in resp_json
    assert ep.RETURN in resp_json


@patch('data.manuscript.update_state', autospec=True, side_effect=ValueError("Mocked Exception"))
def test_update_state_invalid_action(mock_update_state):
    resp = TEST_CLIENT.put(
        f'{ep.MANUSCRIPT_EP}/update_state',
        data=json.dumps(STATE_TEST_DATA),
        content_type='application/json'
    )
    assert resp.status_code == NOT_ACCEPTABLE


# Test data for authentication
AUTH_TEST_DATA = {
    ep.USERNAME: TEST_EMAIL,
    ep.PASSWORD: 'testpassword',
    NAME: "Test Name",
}

@patch('security.auth.register_user', autospec=True, return_value=True)
def test_register_user(mock_register):
    """Test successful user registration"""
    resp = TEST_CLIENT.post(
        f'{ep.AUTH_EP}/register',
        data=json.dumps(AUTH_TEST_DATA),
        content_type='application/json'
    )
    assert resp.status_code == HTTPStatus.CREATED
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert ep.MESSAGE in resp_json
    assert NAME in resp_json
    assert resp_json[NAME] == AUTH_TEST_DATA[NAME]


@patch('security.auth.register_user', autospec=True, return_value=False)
def test_register_user_already_exists(mock_register):
    """Test registration with existing username"""
    resp = TEST_CLIENT.post(
        f'{ep.AUTH_EP}/register',
        data=json.dumps(AUTH_TEST_DATA),
        content_type='application/json'
    )
    assert resp.status_code == HTTPStatus.CONFLICT
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert ep.ERROR in resp_json


LOGIN_TEST_DATA = {
    ep.USERNAME: TEST_EMAIL,
    ep.PASSWORD: 'testpassword',
}


@patch('security.auth.authenticate_user', autospec=True, 
       return_value={ep.USERNAME: LOGIN_TEST_DATA[ep.USERNAME]})
def test_login_user(mock_authenticate):
    """Test successful user login"""
    resp = TEST_CLIENT.post(
        f'{ep.AUTH_EP}/login',
        data=json.dumps(LOGIN_TEST_DATA),
        content_type='application/json'
    )
    assert resp.status_code == HTTPStatus.OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)


@patch('security.auth.authenticate_user', autospec=True, return_value=None)
def test_login_user_invalid_credentials(mock_authenticate):
    """Test login with invalid credentials"""
    resp = TEST_CLIENT.post(
        f'{ep.AUTH_EP}/login',
        data=json.dumps(LOGIN_TEST_DATA),
        content_type='application/json'
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert ep.ERROR in resp_json


@patch('data.manuscript.get_valid_actions_by_state', autospec=True,
       return_value={ms.ASSIGN_REF, ms.REJECT})
def test_get_valid_actions(mock_get_actions):
    """
    Test getting valid actions for a given state.
    """
    resp = TEST_CLIENT.get(f'{ep.MANUSCRIPT_EP}/valid_actions/{ms.SUBMITTED}')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert "valid_actions" in resp_json
    assert isinstance(resp_json["valid_actions"], list)
    assert len(resp_json["valid_actions"]) > 0
    assert all(isinstance(action, str) for action in resp_json["valid_actions"])


@patch('data.manuscript.get_valid_actions_by_state', autospec=True,
       side_effect=KeyError("Invalid state"))
def test_get_valid_actions_invalid_state(mock_get_actions):
    """
    Test getting valid actions for an invalid state.
    """
    resp = TEST_CLIENT.get(f'{ep.MANUSCRIPT_EP}/valid_actions/invalid_state')
    assert resp.status_code == NOT_FOUND


@patch('data.manuscript.get_valid_actions_by_state', autospec=True,
       side_effect=ValueError("Mocked Exception"))
def test_get_valid_actions_error(mock_get_actions):
    """
    Test getting valid actions when an error occurs.
    """
    resp = TEST_CLIENT.get(f'{ep.MANUSCRIPT_EP}/valid_actions/{ms.SUBMITTED}')
    assert resp.status_code == NOT_ACCEPTABLE


@patch('data.manuscript.get_valid_actions_by_state', autospec=True)
def test_get_editor_actions(mock_get_actions):
    """
    Test getting all possible editor actions.
    """
    # Mock the return values for both states
    mock_get_actions.side_effect = [
        {ms.ASSIGN_REF, ms.REJECT},  # SUBMITTED state
        {ms.ACCEPT}  # EDITOR_REV state
    ]
    
    resp = TEST_CLIENT.get(f'{ep.MANUSCRIPT_EP}/editor_actions')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert "editor_actions" in resp_json
    assert isinstance(resp_json["editor_actions"], list)
    assert len(resp_json["editor_actions"]) > 0
    assert all(isinstance(action, str) for action in resp_json["editor_actions"])
    # Verify that actions from both states are included
    assert ms.ASSIGN_REF in resp_json["editor_actions"]
    assert ms.ACCEPT in resp_json["editor_actions"]


@patch('data.manuscript.get_valid_actions_by_state', autospec=True,
       return_value={ms.ACCEPT, ms.REJECT, ms.ACCEPT_WITH_REVISIONS})
def test_get_referee_actions(mock_get_actions):
    """
    Test getting all possible referee actions.
    """
    resp = TEST_CLIENT.get(f'{ep.MANUSCRIPT_EP}/referee_actions')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert "referee_actions" in resp_json
    assert isinstance(resp_json["referee_actions"], list)
    assert len(resp_json["referee_actions"]) > 0
    assert all(isinstance(action, str) for action in resp_json["referee_actions"])
    # Verify that referee-specific actions are included
    assert ms.ACCEPT in resp_json["referee_actions"]
    assert ms.REJECT in resp_json["referee_actions"]
    assert ms.ACCEPT_WITH_REVISIONS in resp_json["referee_actions"]


@patch('data.manuscript.search_by_title', autospec=True,
       return_value={'Test Manuscript': {'title': 'Test Manuscript'}})
def test_search_manuscripts_by_title(mock_search):
    """
    Test searching manuscripts by title.
    """
    resp = TEST_CLIENT.get(f'{ep.MANUSCRIPT_EP}?title=Test')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert 'Test Manuscript' in resp_json
    assert resp_json['Test Manuscript']['title'] == 'Test Manuscript'


@patch('data.manuscript.search_by_title', autospec=True,
       return_value={})
def test_search_manuscripts_no_results(mock_search):
    """
    Test searching manuscripts when no results are found.
    """
    resp = TEST_CLIENT.get(f'{ep.MANUSCRIPT_EP}?title=Nonexistent')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert len(resp_json) == 0


@patch('data.manuscript.read', autospec=True,
       return_value={'All Manuscripts': {'title': 'All Manuscripts'}})
def test_get_all_manuscripts_no_search(mock_read):
    """
    Test getting all manuscripts when no search term is provided.
    """
    resp = TEST_CLIENT.get(ep.MANUSCRIPT_EP)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert 'All Manuscripts' in resp_json
    assert resp_json['All Manuscripts']['title'] == 'All Manuscripts'


def test_dev_status():
    resp = TEST_CLIENT.get('/dev/status')
    assert resp.status_code == HTTPStatus.OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert resp_json['status'] == 'running'
    assert 'server_time' in resp_json
    assert resp_json['environment'] == 'development'
    assert resp_json['version'] == '1.0.0'


def test_dev_config():
    resp = TEST_CLIENT.get('/dev/config')
    assert resp.status_code == HTTPStatus.OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert resp_json['environment'] == 'development'
    assert resp_json['debug_mode'] is True
    assert resp_json['python_version'] == platform.python_version()
    assert resp_json['maintainer'] == 'Chelsea Chen'
    

@patch('data.people.read_one', autospec=True, return_value={
    NAME: 'Alice',
    EMAIL: 'alice@example.com',
    AFFILIATION: 'Wonderland',
    ROLES: ['ED'],
    BIO: 'Curious Adventurer'
})
def test_person_detail_get_success(mock_read_one):
    """GET /people/<user_id> returns the person when found"""
    resp = TEST_CLIENT.get(f'{ep.PEOPLE_EP}/alice-id')
    assert resp.status_code == HTTPStatus.OK
    data = resp.get_json()
    assert isinstance(data, dict)
    assert data[NAME] == 'Alice'
    assert data[EMAIL] == 'alice@example.com'
    assert data[AFFILIATION] == 'Wonderland'
    assert data[ROLES] == ['ED']
    assert data[BIO] == 'Curious Adventurer'


@patch('data.people.read_one', autospec=True, return_value=None)
def test_person_detail_get_not_found(mock_read_one):
    """GET /people/<user_id> returns 404 when not found"""
    resp = TEST_CLIENT.get(f'{ep.PEOPLE_EP}/no-such-id')
    assert resp.status_code == HTTPStatus.NOT_FOUND


@patch('data.people.read_one', autospec=True, return_value=GOOD_USER_RECORD)
@patch('data.people.update', autospec=True, return_value='yw5490@nyu.edu')
def test_person_detail_put_success(mock_update, mock_read_one):
    """PUT /people/<user_id> updates and returns the updated email"""
    payload = {
        NAME: 'Bob',
        AFFILIATION: 'Builder Inc.',
        BIO: 'Can we fix it? Yes we can!'
    }
    resp = TEST_CLIENT.put(
        f'{ep.PEOPLE_EP}/yw5490@nyu.edu',
        data=json.dumps(payload),
        content_type='application/json',
        headers=AUTH_HEADERS
    )
    assert resp.status_code == HTTPStatus.OK
    assert resp.get_json() == 'yw5490@nyu.edu'


@patch('data.people.read_one', autospec=True, return_value=GOOD_USER_RECORD)
@patch('data.people.delete', autospec=True, return_value='yw5490@nyu.edu')
def test_person_detail_delete_success(mock_delete, mock_read_one):
    """DELETE /people/<user_id> removes the person and returns the email"""
    resp = TEST_CLIENT.delete(
        f'{ep.PEOPLE_EP}/yw5490@nyu.edu',
        headers=AUTH_HEADERS
    )
    assert resp.status_code == HTTPStatus.OK
    assert resp.get_json() == 'yw5490@nyu.edu'


@patch('data.people.read_one', autospec=True, return_value=GOOD_USER_RECORD)
@patch('data.people.delete', autospec=True, return_value=None)
def test_person_detail_delete_not_found(mock_delete, mock_read_one):
    """DELETE /people/<user_id> returns 404 when the person does not exist"""
    resp = TEST_CLIENT.delete(
        f'{ep.PEOPLE_EP}/no-such-id',
        headers=AUTH_HEADERS
    )
    assert resp.status_code == HTTPStatus.NOT_FOUND


TEST_COMMENT_ID = "112233xxyy"
TEST_COMMENT_TEXT = "This is a test comment for Referee revisions."

COMMENT_TEST_DATA = {
    cmt.MANUSCRIPT_ID: TEST_MANU_ID,
    cmt.EDITOR_ID: TEST_EMAIL,
    cmt.TEXT: TEST_COMMENT_TEXT
}

COMMENT_UPDATE_TEST_DATA = {
    cmt.COMMENT_ID: TEST_COMMENT_ID,
    cmt.TEXT: "Updated revision text"
}

@patch('security.security.requires_permission', lambda *args, **kwargs: lambda f: f)
@patch('data.comment.read_all', autospec=True,
       return_value=[{cmt.COMMENT_ID: TEST_COMMENT_ID, cmt.TEXT: TEST_COMMENT_TEXT}])
def test_read_comments(mock_read_all):
    """Test reading all comments."""
    resp = TEST_CLIENT.get(ep.COMMENT_EP)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, list)
    assert len(resp_json) > 0
    assert resp_json[0][cmt.COMMENT_ID] == TEST_COMMENT_ID
    assert resp_json[0][cmt.TEXT] == TEST_COMMENT_TEXT

@patch('security.security.requires_permission', lambda *args, **kwargs: lambda f: f)
@patch('data.comment.read_one', autospec=True,
       return_value={cmt.COMMENT_ID: TEST_COMMENT_ID, cmt.TEXT: TEST_COMMENT_TEXT})
def test_read_one_comment(mock_read_one):
    """Test reading a single comment by ID."""
    resp = TEST_CLIENT.get(f'{ep.COMMENT_EP}/{TEST_COMMENT_ID}')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert resp_json[cmt.COMMENT_ID] == TEST_COMMENT_ID
    assert resp_json[cmt.TEXT] == TEST_COMMENT_TEXT

@patch('security.security.requires_permission', lambda *args, **kwargs: lambda f: f)
@patch('data.comment.read_one', autospec=True, return_value=None)
def test_read_one_comment_not_found(mock_read_one):
    """Test reading a non-existent comment."""
    resp = TEST_CLIENT.get(f'{ep.COMMENT_EP}/nonexistent')
    assert resp.status_code == NOT_FOUND



GOOD_EDITOR_USER = {
    "email": TEST_EMAIL,
    "roles": ["ED"],
    "name": "Editor User"
}

@patch('data.people.read_one', return_value=GOOD_EDITOR_USER)
@patch('data.comment.read_one')
@patch('data.comment.delete')
def test_delete_comment(mock_delete, mock_read_one, mock_read_user):
    """Test deleting a comment."""
    mock_read_one.side_effect = [
        {cmt.COMMENT_ID: TEST_COMMENT_ID, cmt.TEXT: "Exists"},
        None
    ]
    mock_delete.return_value = TEST_COMMENT_ID

    resp = TEST_CLIENT.delete(f"{ep.COMMENT_EP}/{TEST_COMMENT_ID}", headers=AUTH_HEADERS)
    assert resp.status_code == OK
    mock_delete.assert_called_once_with(TEST_COMMENT_ID)

@patch('data.people.read_one', return_value=GOOD_EDITOR_USER)
@patch('data.comment.create')
@patch('data.comment.read_one')
def test_create_comment(mock_read_one, mock_create, mock_read_user):
    """Test creating a comment."""
    new_comment_id = "new_comment_123"
    mock_create.return_value = new_comment_id
    created_comment_data = {
        cmt.COMMENT_ID: new_comment_id,
        cmt.MANUSCRIPT_ID: TEST_MANU_ID,
        cmt.EDITOR_ID: TEST_EMAIL,
        cmt.TEXT: "This is a new test comment.",
    }
    mock_read_one.return_value = created_comment_data

    comment_data = {
        cmt.MANUSCRIPT_ID: TEST_MANU_ID,
        cmt.EDITOR_ID: TEST_EMAIL,
        cmt.TEXT: "This is a new test comment.",
    }
    resp = TEST_CLIENT.put(f"{ep.COMMENT_EP}/create", json=comment_data, headers=AUTH_HEADERS)

    assert resp.status_code == OK
    data = resp.get_json()
    assert data[ep.RETURN] == new_comment_id

    mock_create.assert_called_once_with(
        comment_data[cmt.MANUSCRIPT_ID],
        comment_data[cmt.EDITOR_ID],
        comment_data[cmt.TEXT]
    )
    comment = cmt.read_one(new_comment_id)
    assert comment is not None
    assert comment[cmt.TEXT] == comment_data[cmt.TEXT]

@patch('data.people.read_one', return_value=GOOD_EDITOR_USER)
@patch('data.comment.create', side_effect=ValueError("Invalid manuscript ID"))
def test_create_comment_failed(mock_create, mock_read_user):
    """Test creating a comment with invalid data (non-existent manuscript)."""
    comment_data = {
        cmt.MANUSCRIPT_ID: "invalid_manuscript_id",
        cmt.EDITOR_ID: TEST_EMAIL,
        cmt.TEXT: "This comment should fail.",
    }
    resp = TEST_CLIENT.put(f"{ep.COMMENT_EP}/create", json=comment_data, headers=AUTH_HEADERS)
    assert resp.status_code == NOT_ACCEPTABLE

@patch('data.people.read_one', return_value=GOOD_EDITOR_USER)
@patch('data.comment.update')
@patch('data.comment.read_one')
def test_update_comment(mock_read_one, mock_update, mock_read_user):
    """Test updating a comment."""
    mock_update.return_value = TEST_COMMENT_ID
    updated_content = "Updated comment content."
    updated_comment_data = {
        cmt.COMMENT_ID: TEST_COMMENT_ID,
        cmt.TEXT: updated_content
    }
    mock_read_one.return_value = updated_comment_data

    update_data = {
        cmt.COMMENT_ID: TEST_COMMENT_ID,
        cmt.TEXT: updated_content
    }
    resp = TEST_CLIENT.put(f"{ep.COMMENT_EP}/update", json=update_data, headers=AUTH_HEADERS)
    assert resp.status_code == OK
    data = resp.get_json()
    assert data[ep.RETURN] == TEST_COMMENT_ID

    mock_update.assert_called_once_with(TEST_COMMENT_ID, updated_content)
    updated_comment = cmt.read_one(TEST_COMMENT_ID)
    assert updated_comment is not None
    assert updated_comment[cmt.TEXT] == updated_content

@patch('data.people.read_one', return_value=GOOD_EDITOR_USER)
@patch('data.comment.update', side_effect=ValueError("Cannot update non-text fields"))
def test_update_comment_failed(mock_update, mock_read_user):
    """Test updating a comment with invalid data."""
    update_data = {
        cmt.COMMENT_ID: TEST_COMMENT_ID,
        cmt.TEXT: "Trying to fail update",
    }
    resp = TEST_CLIENT.put(f"{ep.COMMENT_EP}/update", json=update_data, headers=AUTH_HEADERS)
    assert resp.status_code == NOT_ACCEPTABLE