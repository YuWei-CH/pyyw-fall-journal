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

from data.people import NAME, AFFILIATION, EMAIL

import server.endpoints as ep

TEST_CLIENT = ep.app.test_client()

import data.people as ppl
import data.tests.test_people as ppl_test
import data.tests.test_text as txt_test
import data.text as txt
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


def test_delete_people():
    resp = TEST_CLIENT.delete(f'{ep.PEOPLE_EP}/{ppl.DEL_EMAIL}')
    resp_json = resp.get_json()
    assert resp_json[ep.DELETED] == ppl.DEL_EMAIL


def test_read_text():
    resp = TEST_CLIENT.get(ep.TEXT_EP)
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    for key in resp_json:
        assert isinstance(key, str)


CREATE_TEST_DATA = {
    NAME: "Test Name",
    AFFILIATION: "Test Affiliation",
    EMAIL: ppl_test.ADD_EMAIL,
}


def test_create_people():
    resp = TEST_CLIENT.put(
        f'{ep.PEOPLE_EP}/create',
        data=json.dumps(CREATE_TEST_DATA),
        content_type='application/json'
    )
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert resp_json[ep.RETURN] == ppl_test.ADD_EMAIL


UPDATE_NAME_TEST_DATA = {
    EMAIL: ppl.TEST_EMAIL,
    ep.FIELD: NAME,
    ep.VALUE: "Yirong Wang",
}


def test_update_name():
    resp = TEST_CLIENT.put(
        f'{ep.PEOPLE_EP}/update',
        data=json.dumps(UPDATE_NAME_TEST_DATA),
        content_type='application/json'
    )
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert resp_json[ep.RETURN] == ppl.TEST_EMAIL


UPDATE_AFFILIATION_TEST_DATA = {
    EMAIL: ppl.TEST_EMAIL,
    ep.FIELD: AFFILIATION,
    ep.VALUE: "USC",
}


def test_update_affiliation():
    resp = TEST_CLIENT.put(
        f'{ep.PEOPLE_EP}/update',
        data=json.dumps(UPDATE_AFFILIATION_TEST_DATA),
        content_type='application/json'
    )
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert resp_json[ep.RETURN] == ppl.TEST_EMAIL


UPDATE_TEST_DATA_INVALID = {
    EMAIL: ppl.TEST_EMAIL,
    ep.FIELD: "Invalid Field. ",
    ep.VALUE: "Do not care about value. ",
}


def test_update_invalid_field():
    resp = TEST_CLIENT.put(
        f'{ep.PEOPLE_EP}/update',
        data=json.dumps(UPDATE_TEST_DATA_INVALID),
        content_type='application/json'
    )
    resp_json = resp.get_json()
    assert "ValueError" in resp_json[ep.MESSAGE]

TEXT_CREATE_TEST_DATA = {
    TITLE: "Test Text",
    TEXT: "Hello, World!",
    PAGE_NUMBER: txt_test.Contact_KEY,
}


def test_create_text():
    resp = TEST_CLIENT.put(
        f'{ep.TEXT_EP}/create',
        data=json.dumps(TEXT_CREATE_TEST_DATA),
        content_type='application/json'
    )
    resp_json = resp.get_json()
    assert isinstance(resp_json, dict)
    assert resp_json[ep.RETURN] == txt_test.Contact_KEY


def test_delete_text():
    # Ensure the text entry exists before deleting
    texts = txt.read()
    assert txt.DEL_PAGE_NUMBER in texts

    # Send DELETE request
    resp = TEST_CLIENT.delete(f'{ep.TEXT_EP}/{txt.DEL_PAGE_NUMBER}')
    resp_json = resp.get_json()
    assert resp.status_code == OK
    assert resp_json[ep.DELETED] == txt.DEL_PAGE_NUMBER


UPDATE_TEXT_DATA = {
    txt.PAGE_NUMBER: txt.TEST_PAGE_NUMBER,
    txt.TITLE: "Updated Title",
    txt.TEXT: "Updated Text",
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
