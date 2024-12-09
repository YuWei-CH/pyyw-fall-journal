"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""
from http import HTTPStatus

from flask import Flask, request
from flask_restx import Resource, Api, fields  # Namespace, fields
from flask_cors import CORS

import werkzeug.exceptions as wz

import data.people as ppl
import data.text as txt

app = Flask(__name__)
CORS(app)
api = Api(app)

ENDPOINT_EP = '/endpoints'
ENDPOINT_RESP = 'Available endpoints'

HELLO_EP = '/hello'
HELLO_RESP = 'hello'

TITLE_EP = '/title'
PEOPLE_EP = '/people'

TITLE_RESP = 'Title'
TITLE = 'Jobless Computer Science Student Analysis (JCSS)'
DATE = '2024-09-24'
DATE_RESP = 'Date'
EDITOR = 'yw5490@nyu.edu'
EDITOR_RESP = 'Editor'
PUBLISHER = 'MisteryForceFromEast'
PUBLISHER_RESP = 'Publisher'

MESSAGE = 'message'
RETURN = 'return'
DELETED = 'Deleted'

TEXT_EP = '/text'

FIELD = 'field'
VALUE = 'value'

ROLE = 'role'


@api.route(HELLO_EP)
class HelloWorld(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def get(self):
        """
        A trivial endpoint to see if the server is running.
        """
        return {HELLO_RESP: 'world'}


@api.route(ENDPOINT_EP)
class Endpoints(Resource):
    """
    This class will serve as live, fetchable documentation of what endpoints
    are available in the system.
    """
    def get(self):
        """
        The `get()` method will return a sorted list of available endpoints.
        """
        endpoints = sorted(rule.rule for rule in api.app.url_map.iter_rules())
        return {"Available endpoints": endpoints}


@api.route(TITLE_EP)
class JournalTitle(Resource):
    """
    This class handles creating, reading, updating
    and deleting the journal title.
    """
    def get(self):
        """
        Retrieve the journal title.
        """
        return {TITLE_RESP: TITLE,
                EDITOR_RESP: EDITOR,
                DATE_RESP: DATE,
                PUBLISHER_RESP: PUBLISHER}


@api.route(PEOPLE_EP)
class People(Resource):
    """
    This class handles creating, reading, updating
    and deleting journal people.
    """
    def get(self):
        """
        Retrieve the journal people.
        """
        return ppl.read()


@api.route(f'{PEOPLE_EP}/<email>')
class Person(Resource):
    """
    This class handles reading and deleting a journal person.
    """
    def get(self, email):
        """
        Retrieve a journal person.
        """
        person = ppl.read_one(email)
        if person:
            return person
        else:
            raise wz.NotFound(f'No such record: {email}')

    @api.response(HTTPStatus.OK, 'Success.')
    @api.response(HTTPStatus.NOT_FOUND, 'No such person.')
    def delete(self, email):
        ret = ppl.delete(email)
        if ret is not None:
            return {'Deleted': ret}
        else:
            raise wz.NotFound(f'No such person: {email}')


PEOPLE_CREATE_FLDS = api.model('AddNewPeopleEntry', {
    ppl.NAME: fields.String,
    ppl.EMAIL: fields.String,
    ppl.AFFILIATION: fields.String,
    ppl.ROLES: fields.String,
})


@api.route(f'{PEOPLE_EP}/create')
class PersonCreate(Resource):
    """
    Add a person to the journal db.
    """
    @api.response(HTTPStatus.OK, 'Success. ')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable. ')
    @api.expect(PEOPLE_CREATE_FLDS)
    def put(self):
        """
        Add a person.
        """
        try:
            name = request.json.get(ppl.NAME)
            affiliation = request.json.get(ppl.AFFILIATION)
            email = request.json.get(ppl.EMAIL)
            role = request.json.get(ppl.ROLES)
            ret = ppl.create(name, affiliation, email, role)
        except Exception as err:
            raise wz.NotAcceptable(f'Could not add person: '
                                   f'{err=}')
        return {
            MESSAGE: 'Person added!',
            RETURN: ret,
        }


PEOPLE_UPDATE_FLDS = api.model('UpdatePeopleEntry', {
    ppl.EMAIL: fields.String,
    ppl.NAME: fields.String,
    ppl.AFFILIATION: fields.String,
})


@api.route(f'{PEOPLE_EP}/update')
class PersonUpdate(Resource):
    """
    This class handles the update of a person's information.
    """
    @api.response(HTTPStatus.OK, 'Success. ')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable. ')
    @api.expect(PEOPLE_UPDATE_FLDS)
    def put(self):
        """
        Update person information.
        """
        try:
            email = request.json.get(ppl.EMAIL)
            name = request.json.get(ppl.NAME)
            affiliation = request.json.get(ppl.AFFILIATION)
            ret = ppl.update(email, name, affiliation)
        except Exception as err:
            raise wz.NotAcceptable(f'Could not update person: '
                                   f'{err=}')
        return {
            MESSAGE: f'{email} updated!',
            RETURN: ret,
        }


PEOPLE_ROLE_UPDATE_FLDS = api.model('UpdateRoleEntry', {
    ppl.EMAIL: fields.String,
    ROLE: fields.String,
})


@api.route(f'{PEOPLE_EP}/add_role')
class PersonAddRole(Resource):
    """
    This class handles the update of a people's role (ADD).
    """
    @api.response(HTTPStatus.OK, 'Success. ')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable. ')
    @api.expect(PEOPLE_ROLE_UPDATE_FLDS)
    def put(self):
        """
        Add people role.
        """
        try:
            email = request.json.get(ppl.EMAIL)
            role = request.json.get(ROLE)
            ret = ppl.add_role(email, role)
        except Exception as err:
            raise wz.NotAcceptable(f'Could not add role: {err}')
        return {
            MESSAGE: f'{role} added for {email}!',
            RETURN: ret,
        }


@api.route(f'{PEOPLE_EP}/delete_role')
class PersonDeleteRole(Resource):
    """
    This class handles the deletion of a people's role (DELETE).
    """
    @api.response(HTTPStatus.OK, 'Success. ')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable. ')
    @api.expect(PEOPLE_ROLE_UPDATE_FLDS)
    def delete(self):
        """
        Delete people role.
        """
        try:
            email = request.json.get(ppl.EMAIL)
            role = request.json.get(ROLE)
            ret = ppl.delete_role(email, role)
        except Exception as err:
            raise wz.NotAcceptable(f'Could not delete role: {err}')
        return {
            MESSAGE: f'{role} deleted for {email}!',
            RETURN: ret,
        }


@api.route(TEXT_EP)
class Texts(Resource):
    """
    This class handles reading text.
    """
    def get(self):
        """
        Retrieve the journal text.
        """
        return txt.read()


TEXT_CREATE_FLDS = api.model('AddNewTextEntry', {
    txt.TITLE: fields.String,
    txt.TEXT: fields.String,
    txt.PAGE_NUMBER: fields.String,
})


@api.route(f'{TEXT_EP}/create')
class TextCreate(Resource):
    """
    Add a Text to the journal db.
    """
    @api.response(HTTPStatus.OK, 'Success. ')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable. ')
    @api.expect(TEXT_CREATE_FLDS)
    def put(self):
        """
        Add a text.
        """
        try:
            title = request.json.get(txt.TITLE)
            text = request.json.get(txt.TEXT)
            page_number = request.json.get(txt.PAGE_NUMBER)
            ret = txt.create(page_number, title, text)
        except Exception as err:
            raise wz.NotAcceptable(f'Could not add text: '
                                   f'{err=}')
        return {
            MESSAGE: 'Text added!',
            RETURN: ret,
        }


@api.route(f'{TEXT_EP}/<page_number>')
class Text(Resource):
    """
    This class handles reading and deleting a text through a page number.
    """
    def get(self, page_number):
        """
        Retrieve a text page.
        """
        text = txt.read_one(page_number)
        if text:
            return text
        else:
            raise wz.NotFound(f'No such page: {page_number}')

    @api.response(HTTPStatus.OK, 'Success.')
    @api.response(HTTPStatus.NOT_FOUND, 'No such text.')
    def delete(self, page_number):
        ret = txt.delete(page_number)
        if ret is not None:
            return {DELETED: ret}
        else:
            raise wz.NotFound(f'No such text: {page_number}')


TEXT_UPDATE_FLDS = api.model('UpdateTextEntry', {
    txt.PAGE_NUMBER: fields.String,
    FIELD: fields.String,
    VALUE: fields.String,
})


@api.route(f'{TEXT_EP}/update')
class TextUpdate(Resource):
    """
    This class handles the update of a text's information.
    """
    @api.response(HTTPStatus.OK, 'Success. ')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable. ')
    @api.expect(TEXT_UPDATE_FLDS)
    def put(self):
        """
        Update text information.
        """
        try:
            page_number = request.json.get(txt.PAGE_NUMBER)
            field = request.json.get(FIELD)
            value = request.json.get(VALUE)
            txt.update(page_number, field, value)
        except Exception as err:
            raise wz.NotAcceptable(f'Could not update text: '
                                   f'{err=}')
        return {
            MESSAGE: f'{field} updated for {page_number}!',
            RETURN: page_number,
        }


MASTHEAD = 'Masthead'


@api.route(f'{PEOPLE_EP}/masthead')
class Masthead(Resource):
    """
    Get a journal's masthead.
    """
    def get(self):
        return {MASTHEAD: ppl.get_masthead()}
