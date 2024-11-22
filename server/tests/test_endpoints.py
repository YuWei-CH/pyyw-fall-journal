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
import data.tests.test_people as ppl_test
import data.tests.test_text as txt_test
import data.text as txt
import data.roles as rls
from data.text import *

def test_hello():
    resp = TEST_CLIENT.get(ep.HELLO_EP)
    resp_json = resp.get_json()
    assert ep.HELLO_RESP in resp_json


def test_title():
    resp = TEST_CLIENT.get(ep.TITLE_EP)
    resp_json = resp.get_json()
    assert ep.TITLE_RESP in resp_json
    assert isinstance(resp_json[ep.TITLE_RESP], str)
    assert len(resp_json[ep.TITLE_RESP]) > 0


def test_read_people():
    resp = TEST_CLIENT.get(ep.PEOPLE_EP)
    resp_json = resp.get_json()
    for _id, person in resp_json.items():
        assert isinstance(_id, str)
        assert len(_id) > 0
        assert NAME in person


@patch('data.text.read', autospec=True,
       return_value={'page_number': {TITLE: 'Test Title', TEXT: 'Test Text'}})
def test_read_text(mock_read):
    resp = TEST_CLIENT.get(ep.TEXT_EP)
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    for _page_number, text in resp_json.items():
        assert isinstance(_page_number, str)
        assert len(_page_number) > 0
        assert TITLE in text
        assert text[TITLE] == 'Test Title'
        assert TEXT in text
        assert text[TEXT] == 'Test Text'


New_Email = "new@nyu.edu"
CREATE_TEST_DATA = {
    NAME: "Test Name",
    AFFILIATION: "Test Affiliation",
    EMAIL: New_Email,
    ROLES: rls.TEST_CODE
}


def test_create_people():
    resp = TEST_CLIENT.put(
        f'{ep.PEOPLE_EP}/create',
        data=json.dumps(CREATE_TEST_DATA),
        content_type='application/json'
    )
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert resp_json[ep.RETURN] == New_Email


def test_delete_people():
    resp = TEST_CLIENT.delete(f'{ep.PEOPLE_EP}/{New_Email}')
    resp_json = resp.get_json()
    assert resp_json[ep.DELETED] == New_Email


UPDATE_PEOPLE_DATA = {
    EMAIL: ppl.TEST_EMAIL,
    ep.FIELD: NAME,
    ep.VALUE: "Yirong Wang",
}


def test_update_people():
    resp = TEST_CLIENT.put(
        f'{ep.PEOPLE_EP}/update',
        data=json.dumps(UPDATE_PEOPLE_DATA),
        content_type='application/json'
    )
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert resp_json[ep.RETURN] == ppl.TEST_EMAIL


ADD_TEST_ROLE_DATA = {
    EMAIL: ppl.TEST_EMAIL,
    ep.ROLE: "RE"
}

def test_add_role():
    resp = TEST_CLIENT.put(
        f'{ep.PEOPLE_EP}/add_role',
        data=json.dumps(ADD_TEST_ROLE_DATA),
        content_type='application/json'
    )
    resp_json = resp.get_json()
    assert resp_json[ep.RETURN] == ppl.TEST_EMAIL


New_Page_Number = "Next Page" 
TEXT_CREATE_TEST_DATA = {
    TITLE: "Test Text",
    TEXT: "Hello, World!",
    PAGE_NUMBER: New_Page_Number,
}


def test_create_text():
    resp = TEST_CLIENT.put(
        f'{ep.TEXT_EP}/create',
        data=json.dumps(TEXT_CREATE_TEST_DATA),
        content_type='application/json'
    )
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert resp_json[ep.RETURN] == New_Page_Number


def test_delete_text():
    # Ensure the text entry exists before deleting
    texts = txt.read()
    assert New_Page_Number in texts

    # Send DELETE request
    resp = TEST_CLIENT.delete(f'{ep.TEXT_EP}/{New_Page_Number}')
    resp_json = resp.get_json()
    assert resp.status_code == OK
    assert resp_json[ep.DELETED] == New_Page_Number


UPDATE_TEXT_DATA = {
    txt.PAGE_NUMBER: txt.TEST_PAGE_NUMBER,
    ep.FIELD: txt.TITLE, 
    ep.VALUE: "New Test Title",
}


def test_update_text():
    resp = TEST_CLIENT.put(
        f'{ep.TEXT_EP}/update',
        data=json.dumps(UPDATE_TEXT_DATA),
        content_type='application/json'
    )
    assert resp.status_code == OK
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert resp_json[ep.RETURN] == txt.TEST_PAGE_NUMBER
