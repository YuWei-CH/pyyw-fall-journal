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
