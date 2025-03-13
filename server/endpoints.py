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
import data.roles as rls
import data.text as txt
import data.manuscript as ms
import security.auth as auth

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

ROLES_EP = '/roles'
ROLE = 'role'

MANUSCRIPT_EP = '/manuscript'

ACTION = 'action'
REFEREE = 'referee'

AUTH_EP = '/auth'

AUTH_FIELDS = api.model('AuthFields', {
    'username': fields.String(required=True),
    'password': fields.String(required=True),
})


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
        return {
            TITLE_RESP: TITLE,
            EDITOR_RESP: EDITOR,
            DATE_RESP: DATE,
            PUBLISHER_RESP: PUBLISHER
        }


@api.route(ROLES_EP)
class Roles(Resource):
    """
    This class handles reading person roles.
    """
    def get(self):
        """
        Retrieve the journal person roles.
        """
        return rls.read()


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
        """
        Delete a person by email.
        """
        ret = ppl.delete(email)
        if ret is not None:
            return {DELETED: ret}
        else:
            raise wz.NotFound(f'No such person: {email}')


PEOPLE_CREATE_FLDS = api.model('AddNewPeopleEntry', {
    ppl.NAME: fields.String,
    ppl.EMAIL: fields.String,
    ppl.AFFILIATION: fields.String,
    ppl.ROLES: fields.String,
    ppl.BIO: fields.String(required=False),
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
            bio = request.json.get(ppl.BIO, "")
            ret = ppl.create(name, affiliation, email, role, bio)
        except Exception as err:
            raise wz.NotAcceptable(f'Could not add person: {err=}')
        return {
            MESSAGE: 'Person added!',
            RETURN: ret,
        }


PEOPLE_UPDATE_FLDS = api.model('UpdatePeopleEntry', {
    ppl.EMAIL: fields.String,
    ppl.NAME: fields.String,
    ppl.AFFILIATION: fields.String,
    ppl.BIO: fields.String(required=False),
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
            bio = request.json.get(ppl.BIO)
            ret = ppl.update(email, name, affiliation, bio)
        except Exception as err:
            raise wz.NotAcceptable(f'Could not update person: {err=}')
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


TEXT_FLDS = api.model('TextEntry', {
    txt.PAGE_NUMBER: fields.String,
    txt.TITLE: fields.String,
    txt.TEXT: fields.String,
})


@api.route(f'{TEXT_EP}/create')
class TextCreate(Resource):
    """
    Add a Text to the journal db.
    """
    @api.response(HTTPStatus.OK, 'Success. ')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable. ')
    @api.expect(TEXT_FLDS)
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
            raise wz.NotAcceptable(f'Could not add text: {err=}')
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
        """
        Delete a text by page number.
        """
        ret = txt.delete(page_number)
        if ret is not None:
            return {DELETED: ret}
        else:
            raise wz.NotFound(f'No such text: {page_number}')


@api.route(f'{TEXT_EP}/update')
class TextUpdate(Resource):
    """
    This class handles the update of a text's information.
    """
    @api.response(HTTPStatus.OK, 'Success. ')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable. ')
    @api.expect(TEXT_FLDS)
    def put(self):
        """
        Update text information.
        """
        try:
            page_number = request.json.get(txt.PAGE_NUMBER)
            title = request.json.get(txt.TITLE)
            text = request.json.get(txt.TEXT)
            ret = txt.update(page_number, title, text)
        except Exception as err:
            raise wz.NotAcceptable(f'Could not update text: {err=}')
        return {
            MESSAGE: f'{page_number} updated!',
            RETURN: ret,
        }


MASTHEAD = 'Masthead'


@api.route(f'{PEOPLE_EP}/masthead')
class Masthead(Resource):
    """
    Get a journal's masthead.
    """
    def get(self):
        """
        Retrieve a journal's masthead.
        """
        return {MASTHEAD: ppl.get_masthead()}


@api.route(MANUSCRIPT_EP)
class Manuscripts(Resource):
    """
    This class handles creating, reading, updating
    and deleting manuscripts.
    """
    def get(self):
        """
        Retrieve all manuscripts.
        """
        return ms.read()


@api.route(f'{MANUSCRIPT_EP}/<manu_id>')
class Manuscript(Resource):
    """
    This class handles reading and deleting a manuscript.
    """
    def get(self, manu_id):
        """
        Retrieve a single manuscript by _id.
        """
        manu = ms.read_one(manu_id)
        if manu:
            return manu
        else:
            raise wz.NotFound(f'No such manuscript with _id: {manu_id}')

    @api.response(HTTPStatus.OK, 'Success.')
    @api.response(HTTPStatus.NOT_FOUND, 'No such manuscript.')
    def delete(self, manu_id):
        """
        Delete a manuscript by _id.
        """
        ret = ms.delete(manu_id)
        if ret is not None:
            return {DELETED: ret}
        else:
            raise wz.NotFound(f'No such manuscript with _id: {manu_id}')


MANUSCRIPT_FLDS = api.model('ManuscriptEntry', {
    ms.TITLE: fields.String,
    ms.AUTHOR: fields.String,
    ms.AUTHOR_EMAIL: fields.String,
    ms.TEXT: fields.String,
    ms.ABSTRACT: fields.String,
    ms.EDITOR_EMAIL: fields.String,
})


@api.route(f'{MANUSCRIPT_EP}/create')
class ManuscriptCreate(Resource):
    """
    Add a manuscript to the journal db.
    """
    @api.response(HTTPStatus.OK, 'Success.')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable.')
    @api.expect(MANUSCRIPT_FLDS)
    def put(self):
        """
        Add a new manuscript.
        """
        try:
            title = request.json.get(ms.TITLE)
            author = request.json.get(ms.AUTHOR)
            author_email = request.json.get(ms.AUTHOR_EMAIL)
            text = request.json.get(ms.TEXT)
            abstract = request.json.get(ms.ABSTRACT)
            editor_email = request.json.get(ms.EDITOR_EMAIL)
            ret = ms.create(title, author, author_email,
                            text, abstract, editor_email)
        except Exception as err:
            raise wz.NotAcceptable(f'Could not add manuscript: {err=}')
        return {
            MESSAGE: 'Manuscript added!',
            RETURN: ret,
        }


MANUSCRIPT_UPDATE_FLDS = api.model('ManuscriptUpdateEntry', {
    ms.MANU_ID: fields.String,
    ms.TITLE: fields.String,
    ms.AUTHOR: fields.String,
    ms.AUTHOR_EMAIL: fields.String,
    ms.TEXT: fields.String,
    ms.ABSTRACT: fields.String,
    ms.EDITOR_EMAIL: fields.String,
})


@api.route(f'{MANUSCRIPT_EP}/update')
class ManuscriptUpdate(Resource):
    """
    This class handles the update of a manuscript's information.
    """
    @api.response(HTTPStatus.OK, 'Success.')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable.')
    @api.expect(MANUSCRIPT_UPDATE_FLDS)
    def put(self):
        """
        Update manuscript information.
        """
        try:
            manu_id = request.json.get(ms.MANU_ID)
            title = request.json.get(ms.TITLE)
            author = request.json.get(ms.AUTHOR)
            author_email = request.json.get(ms.AUTHOR_EMAIL)
            text = request.json.get(ms.TEXT)
            abstract = request.json.get(ms.ABSTRACT)
            editor_email = request.json.get(ms.EDITOR_EMAIL)
            ret = ms.update(manu_id, title, author, author_email,
                            text, abstract, editor_email)
        except Exception as err:
            raise wz.NotAcceptable(f'Could not update manuscript: {err=}')
        return {
            MESSAGE: f'{manu_id} updated!',
            RETURN: ret,
        }


MANUSCRIPT_UPDATE_STATE_FLDS = api.model('ManuscriptUpdateStateEntry', {
    ms.MANU_ID: fields.String,
    ACTION: fields.String,
    REFEREE: fields.String(required=False),
})


@api.route(f'{MANUSCRIPT_EP}/update_state')
class ManuscriptUpdateState(Resource):
    """
    This class handles the update of a manuscript's state.
    """
    @api.response(HTTPStatus.OK, 'Success.')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable. ')
    @api.expect(MANUSCRIPT_UPDATE_STATE_FLDS)
    def put(self):
        """
        Perform an action on the manuscript's state machine.
        """
        try:
            manu_id = request.json.get(ms.MANU_ID)
            action = request.json.get(ACTION)
            ref = request.json.get(REFEREE)
            if action == ms.ASSIGN_REF or action == ms.DELETE_REF:
                ret = ms.update_state(manu_id, action, ref=ref)
            else:
                ret = ms.update_state(manu_id, action)
        except Exception as err:
            raise wz.NotAcceptable(
                f'Could not update manuscript state: {err=}')
        return {
            MESSAGE: f'{manu_id} state updated!',
            RETURN: ret,
        }


@api.route(f'{AUTH_EP}/register')
class Register(Resource):
    """
    This class handles user registration.
    """
    @api.response(HTTPStatus.CREATED, 'User registered successfully.')
    @api.response(HTTPStatus.CONFLICT, 'Username already exists.')
    @api.expect(AUTH_FIELDS)
    def post(self):
        """
        Register a new user.
        """
        data = request.get_json()
        success = auth.register_user(data['username'], data['password'])
        if success:
            return {
                'message': 'User registered successfully'
            }, HTTPStatus.CREATED
        else:
            return {
                'error': 'Username already exists'
            }, HTTPStatus.CONFLICT


@api.route(f'{AUTH_EP}/login')
class Login(Resource):
    """
    This class handles user authentication.
    """
    @api.response(HTTPStatus.OK, 'Login successful.')
    @api.response(HTTPStatus.UNAUTHORIZED, 'Invalid credentials.')
    @api.expect(AUTH_FIELDS)
    def post(self):
        """
        Authenticate a user.
        """
        data = request.get_json()
        user = auth.authenticate_user(data['username'], data['password'])
        if user:
            return user, HTTPStatus.OK
        else:
            return {'error': 'Invalid credentials'}, HTTPStatus.UNAUTHORIZED
