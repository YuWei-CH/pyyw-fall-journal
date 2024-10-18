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
TITLE_RESP = 'Title'
TITLE = 'Jobless Computer Science Student Analysis (JCSS)'

PEOPLE_EP = '/people'
PUBLISHER = 'MisteryForceFromEast'
PUBLISHER_RESP = 'Publisher'

MESSAGE = 'message'
RETURN = 'return'

TEXT_EP = '/text'

FIELD = 'field'
VALUE = 'value'


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
        return {TITLE_RESP: TITLE}


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


PEOPLE_CREATE_FLDS = api.model('AddNewPeopleEntry', {
    ppl.NAME: fields.String,
    ppl.EMAIL: fields.String,
    ppl.AFFILIATION: fields.String,
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
            ret = ppl.create(name, affiliation, email)
        except Exception as err:
            raise wz.NotAcceptable(f'Could not add person: '
                                   f'{err=}')
        return {
            MESSAGE: 'Person added!',
            RETURN: ret,
        }


@api.route(f'{PEOPLE_EP}/<_id>')
class PersonDelete(Resource):
    @api.response(HTTPStatus.OK, 'Success. ')
    @api.response(HTTPStatus.NOT_FOUND, 'No such person. ')
    def delete(self, _id):
        ret = ppl.delete(_id)
        if ret is not None:
            return {'Deleted': ret}
        else:
            raise wz.NotFound(f'No such person: {_id}')


@api.route(TEXT_EP)
class TEXT(Resource):
    """
    This class handles reading text.
    """
    def get(self):
        """
        Retrieve the journal people.
        """
        return txt.read()


PEOPLE_UPDATE_FLDS = api.model('UpdatePeopleEntry', {
    ppl.EMAIL: fields.String,
    FIELD: fields.String,
    VALUE: fields.String,
})


@api.route(f'{PEOPLE_EP}/update')
class PersonUpdate(Resource):
    """
    This class handles the update of a person's information.
    """
    @api.response(HTTPStatus.OK, 'Success. ')
    @api.response(HTTPStatus.NOT_FOUND, 'No such person. ')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable. ')
    @api.expect(PEOPLE_UPDATE_FLDS)
    def put(self):
        """
        Update person information.
        """
        try:
            field = request.json.get(FIELD)
            value = request.json.get(VALUE)
            email = request.json.get(ppl.EMAIL)
            if field == ppl.NAME:
                ret = ppl.update_name(email, value)
            elif field == ppl.AFFILIATION:
                ret = ppl.update_affiliation(email, value)
            else:
                raise ValueError("Invalid field name. ")
        except Exception as err:
            raise wz.NotAcceptable(f'Could not update person: '
                                   f'{err=}')
        if ret is None:
            raise wz.NotFound(f'No such person: {email}')
        return {
            MESSAGE: f'{field} updated for {email}!',
            RETURN: ret,
        }
