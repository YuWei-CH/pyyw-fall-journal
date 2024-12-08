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

from data.people import NAME, AFFILIATION, EMAIL, ROLES

import server.endpoints as ep

TEST_CLIENT = ep.app.test_client()

import data.people as ppl
import data.text as txt
import data.roles as rls
from data.text import *

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


@patch('data.people.read_one', autospec=True,
       return_value={NAME: 'Joe Schmoe'})
def test_read_one_person(mock_read):
    resp = TEST_CLIENT.get(f'{ep.PEOPLE_EP}/mock_id')
    assert resp.status_code == OK


@patch('data.people.read_one', autospec=True, return_value=None)
def test_read_one_person_not_found(mock_read):
    resp = TEST_CLIENT.get(f'{ep.PEOPLE_EP}/mock_id')
    assert resp.status_code == NOT_FOUND


@patch('data.people.delete', autospec=True, return_value='testEmail@gmail.com')
def test_delete_people(mock_delete):
    resp = TEST_CLIENT.delete(f'{ep.PEOPLE_EP}/mock_email')
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert ep.DELETED in resp_json


@patch('data.people.delete', autospec=True, return_value=None)
def test_delete_people_not_found(mock_delete):
    resp = TEST_CLIENT.delete(f'{ep.PEOPLE_EP}/mock_email')
    assert resp.status_code == NOT_FOUND


CREATE_TEST_DATA = {
    NAME: "Test Name",
    AFFILIATION: "Test Affiliation",
    EMAIL: "testEmail@gmail.com",
    ROLES: rls.TEST_CODE
}

@patch('data.people.create', autospec=True, return_value='testEmail@gmail.com')
def test_create_people(mock_create):
    resp = TEST_CLIENT.put(
        f'{ep.PEOPLE_EP}/create',
        data=json.dumps(CREATE_TEST_DATA),
        content_type='application/json'
    )
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert ep.MESSAGE in resp_json
    assert ep.RETURN in resp_json


@patch('data.people.create', autospec=True, side_effect=ValueError("Mocked Exception"))
def test_create_people_failed(mock_create):
    resp = TEST_CLIENT.put(
        f'{ep.PEOPLE_EP}/create',
        data=json.dumps(CREATE_TEST_DATA),
        content_type='application/json'
    )
    assert resp.status_code == NOT_ACCEPTABLE


UPDATE_PEOPLE_DATA = {
    EMAIL: "testEmail@gmail.com",
    ep.FIELD: NAME,
    ep.VALUE: "Yirong Wang",
}


@patch('data.people.update', autospec=True, return_value='testEmail@gmail.com')
def test_update_people(mock_update):
    resp = TEST_CLIENT.put(
        f'{ep.PEOPLE_EP}/update',
        data=json.dumps(UPDATE_PEOPLE_DATA),
        content_type='application/json'
    )
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert ep.MESSAGE in resp_json
    assert ep.RETURN in resp_json


ADD_DELETE_ROLE_DATA = {
    EMAIL: "testEmail@gmail.com",
    ep.ROLE: rls.TEST_CODE
}


@patch('data.people.add_role', autospec=True, return_value='testEmail@gmail.com')
def test_add_role(mock_add_role):
    resp = TEST_CLIENT.put(
        f'{ep.PEOPLE_EP}/add_role',
        data=json.dumps(ADD_DELETE_ROLE_DATA),
        content_type='application/json'
    )
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert ep.MESSAGE in resp_json
    assert ep.RETURN in resp_json


@patch('data.people.delete_role', autospec=True, return_value='testEmail@gmail.com')
def test_delete_role(mock_delete_role):
    resp = TEST_CLIENT.delete(
        f'{ep.PEOPLE_EP}/delete_role',
        data=json.dumps(ADD_DELETE_ROLE_DATA),
        content_type='application/json'
    )
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert ep.MESSAGE in resp_json
    assert ep.RETURN in resp_json


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


TEXT_CREATE_TEST_DATA = {
    TITLE: "Test Title",
    TEXT: "Test Text",
    PAGE_NUMBER: "TestPageNumber",
}


@patch('data.text.create', autospec=True, return_value='TestPageNumber')
def test_create_text(mock_create):
    resp = TEST_CLIENT.put(
        f'{ep.TEXT_EP}/create',
        data=json.dumps(TEXT_CREATE_TEST_DATA),
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
        data=json.dumps(TEXT_CREATE_TEST_DATA),
        content_type='application/json'
    )
    assert resp.status_code == NOT_ACCEPTABLE


@patch('data.text.delete', autospec=True, return_value='TestPageNumber')
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


UPDATE_TEXT_DATA = {
    txt.PAGE_NUMBER: "TestPageNumber",
    ep.FIELD: txt.TITLE, 
    ep.VALUE: "Test Title",
}


@patch('data.text.update', autospec=True, return_value='TestPageNumber')
def test_update_text(mock_update):
    resp = TEST_CLIENT.put(
        f'{ep.TEXT_EP}/update',
        data=json.dumps(UPDATE_TEXT_DATA),
        content_type='application/json'
    )
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert ep.MESSAGE in resp_json
    assert ep.RETURN in resp_json


@patch('data.text.update', autospec=True, side_effect=ValueError("Mocked Exception"))
def test_update_text_failed(mock_update):
    resp = TEST_CLIENT.put(
        f'{ep.TEXT_EP}/update',
        data=json.dumps(UPDATE_TEXT_DATA),
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