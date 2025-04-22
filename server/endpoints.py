"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""
from http import HTTPStatus

from flask import Flask, request, jsonify
from flask_restx import Resource, Api, fields  # Namespace, fields
from flask_cors import CORS

import werkzeug.exceptions as wz

import data.people as ppl
import data.roles as rls
import data.text as txt
import data.manuscript as ms
import security.auth as auth
import security.security as sec

from datetime import datetime
import platform

# Config for developer endpoints
CONFIG = {
    "ENVIRONMENT": "development",
    "DEBUG": True,
    "VERSION": "1.0.0",
    "MAINTAINER": "Chelsea Chen",
}

app = Flask(__name__)
CORS(app)

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
ERROR = 'error'
DELETED = 'Deleted'

TEXT_EP = '/text'

ROLES_EP = '/roles'
ROLE = 'role'

MANUSCRIPT_EP = '/manuscript'

ACTION = 'action'
REFEREE = 'referee'

AUTH_EP = '/auth'

USERNAME = 'username'
PASSWORD = 'password'

DEV_EP = '/dev'

authorizations = {
    'ApiKeyHeader': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-User-Id',
        'description': 'Your user UUID or email (must have ED/ME roles)'
    }
}

api = Api(
    app,
    version='1.0',
    title='My Journal API',
    description='API for journal management',
    authorizations=authorizations,
    security='ApiKeyHeader'
)


@api.route(f'{DEV_EP}/status')
class DevStatus(Resource):
    """Endpoint for checking basic server status."""
    @api.response(HTTPStatus.OK, 'Server status retrieved successfully.')
    def get(self):
        status_info = {
            'server_time': datetime.now().isoformat(),
            'status': 'running',
            'environment': CONFIG['ENVIRONMENT'],
            'version': CONFIG['VERSION'],
        }
        return jsonify(status_info)


@api.route(f'{DEV_EP}/config')
class DevConfig(Resource):
    """Endpoint for retrieving internal server configuration."""
    @api.response(HTTPStatus.OK,
                  'Server configuration retrieved successfully.')
    def get(self):
        config_info = {
            'environment': CONFIG['ENVIRONMENT'],
            'debug_mode': CONFIG['DEBUG'],
            'python_version': platform.python_version(),
            'maintainer': CONFIG['MAINTAINER'],
        }
        return jsonify(config_info)


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
class PeopleList(Resource):
    """
    This class handles creating, reading, updating
    and deleting journal people.
    """
    def get(self):
        """
        Retrieve the journal people.
        """
        return ppl.read()


@api.route(f'{PEOPLE_EP}/get_all_people')
class PeopleGetAll(Resource):
    def get(self):
        """
        Retrieve all people's name and email in a list.
        """
        return ppl.get_all_people()


PEOPLE_UPDATE_FLDS = api.model('UpdatePeopleEntry', {
    ppl.NAME:       fields.String(required=True),
    ppl.AFFILIATION: fields.String(required=True),
    ppl.BIO:        fields.String(required=False),
})


@api.route(f'{PEOPLE_EP}/<string:user_id>')
class PersonDetail(Resource):
    @api.doc(params={'user_id': 'UUID or email'})
    def get(self, user_id):
        person = ppl.read_one(user_id)
        if not person:
            raise wz.NotFound(f'No such person: {user_id}')
        return person

    @sec.requires_permission('people', 'update', roles=['ED', 'ME'])
    @api.expect(PEOPLE_UPDATE_FLDS)
    def put(self, user_id):
        data = request.get_json(force=True)
        updated = ppl.update(
            user_id,
            data['name'], data['affiliation'], data.get('bio')
        )
        return updated

    @sec.requires_permission('people', 'delete', roles=['ED', 'ME'])
    def delete(self, user_id):
        deleted = ppl.delete(user_id)
        if not deleted:
            raise wz.NotFound(f'No such person: {user_id}')
        return deleted


@api.route(f'{PEOPLE_EP}/<email>')
class Person(Resource):
    """
    This class handles reading journal person.
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


PEOPLE_CREATE_FLDS = api.model('AddNewPeopleEntry', {
    ppl.NAME: fields.String,
    ppl.EMAIL: fields.String,
    ppl.AFFILIATION: fields.String,
    ppl.ROLES: fields.String,
    ppl.BIO: fields.String(required=False),
})


@api.route(f'{PEOPLE_EP}/create')
class PersonCreate(Resource):
    @api.expect(PEOPLE_CREATE_FLDS)
    def post(self):
        all_people = ppl.read()
        if all_people:
            caller = request.headers.get('X-User-Id')
            user = ppl.read_one(caller) if caller else None
            if not user or not set(
                    user.get('roles', [])).intersection({'ED', 'ME'}):
                raise wz.Forbidden(
                    'Only ED/ME may add new people once seeded')
        return ppl.create(
            name=request.json.get(ppl.NAME),
            affiliation=request.json.get(ppl.AFFILIATION),
            bio=request.json.get(ppl.BIO),
            email=request.json.get(ppl.EMAIL),
            role=request.json.get(ppl.ROLES),
        ), HTTPStatus.CREATED


PEOPLE_ROLE_UPDATE_FLDS = api.model('UpdateRoleEntry', {
    ppl.ID: fields.String,
    ROLE: fields.String,
})


@api.route(f'{PEOPLE_EP}/add_role')
class PersonAddRole(Resource):
    @api.response(HTTPStatus.OK, 'Success.')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable.')
    @sec.requires_permission('people', 'create', roles=['ED', 'ME'])
    @api.expect(PEOPLE_ROLE_UPDATE_FLDS)
    def put(self):
        data = request.get_json(force=True)
        try:
            user_id = data[ppl.ID]
            role = data[ROLE]
            updated = ppl.add_role(user_id, role)
            return {
                MESSAGE: f'Role "{role}" added to {user_id}',
                RETURN:  updated
            }, HTTPStatus.OK
        except Exception as err:
            raise wz.NotAcceptable(f'Could not add role: {err}')


@api.route(f'{PEOPLE_EP}/delete_role')
class PersonDeleteRole(Resource):
    @api.response(HTTPStatus.OK, 'Success.')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'Not acceptable.')
    @sec.requires_permission('people', 'create', roles=['ED', 'ME'])
    @api.expect(PEOPLE_ROLE_UPDATE_FLDS)
    def delete(self):
        data = request.get_json(force=True)
        try:
            user_id = data[ppl.ID]
            role = data[ROLE]
            updated = ppl.delete_role(user_id, role)
            return {
                MESSAGE: f'Role "{role}" added to {user_id}',
                RETURN:  updated
            }, HTTPStatus.OK
        except Exception as err:
            raise wz.NotAcceptable(f'Could not delete role: {err}')


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
        Retrieve all manuscripts or search by title.
        If title parameter is provided, returns matching manuscripts.
        Otherwise returns all manuscripts.
        """
        title = request.args.get('title')
        if title:
            return ms.search_by_title(title)
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


AUTH_FIELDS = api.model('AuthFields', {
    USERNAME: fields.String(required=True),
    PASSWORD: fields.String(required=True),
    ppl.NAME: fields.String(required=True),
    ppl.AFFILIATION: fields.String(required=False),
    ppl.BIO: fields.String(required=False),
})


@api.route(f'{AUTH_EP}/register')
class Register(Resource):
    @api.response(HTTPStatus.CREATED, 'User registered successfully.')
    @api.response(HTTPStatus.CONFLICT, 'Username already exists.')
    @api.expect(AUTH_FIELDS)
    def post(self):
        try:
            data = request.get_json()
            print('Received register data:', data)

            kwargs = {
                "username": data[USERNAME],
                "password": data[PASSWORD],
                "name": data[ppl.NAME],
            }

            if ppl.AFFILIATION in data:
                kwargs["affiliation"] = data[ppl.AFFILIATION]

            if ROLE in data:
                kwargs["role"] = data[ROLE]

            if ppl.BIO in data:
                kwargs["bio"] = data[ppl.BIO]

            success = auth.register_user(**kwargs)

            if success:
                return {
                    MESSAGE: 'User registered successfully',
                    ppl.NAME: data[ppl.NAME]
                }, HTTPStatus.CREATED
            else:
                return {
                    ERROR: 'Username already exists'
                }, HTTPStatus.CONFLICT

        except Exception as e:
            print(f'Error in registration: {e}')
            raise wz.InternalServerError(str(e))


LOGIN_FIELDS = api.model('LoginFields', {
    USERNAME: fields.String(required=True),
    PASSWORD: fields.String(required=True),
})


@api.route(f'{AUTH_EP}/login')
class Login(Resource):
    """
    This class handles user authentication.
    """
    @api.response(HTTPStatus.OK, 'Login successful.')
    @api.response(HTTPStatus.UNAUTHORIZED, 'Invalid credentials.')
    @api.expect(LOGIN_FIELDS)
    def post(self):
        """
        Authenticate a user.
        """
        data = request.get_json()
        user = auth.authenticate_user(data[USERNAME], data[PASSWORD])
        if user:
            return user, HTTPStatus.OK
        else:
            return {ERROR: 'Invalid credentials'}, HTTPStatus.UNAUTHORIZED


@api.route(f'{MANUSCRIPT_EP}/valid_actions/<state>')
class ManuscriptValidActions(Resource):
    """
    This class handles getting valid actions for a given manuscript state.
    """
    def get(self, state):
        """
        Get valid actions for a given manuscript state.
        """
        try:
            valid_actions = ms.get_valid_actions_by_state(state)
            return {"valid_actions": list(valid_actions)}
        except KeyError:
            raise wz.NotFound(f'Invalid state: {state}')
        except Exception as err:
            raise wz.NotAcceptable(f'Could not get valid actions: {err=}')


@api.route(f'{MANUSCRIPT_EP}/editor_actions')
class ManuscriptEditorActions(Resource):
    """
    This class handles getting all possible editor actions.
    """
    def get(self):
        """
        Get all possible editor actions.
        """
        # Editor actions: can be taken in SUBMITTED and EDITOR_REV states
        editor_actions = set()
        editor_actions.update(ms.get_valid_actions_by_state(ms.SUBMITTED))
        editor_actions.update(ms.get_valid_actions_by_state(ms.EDITOR_REV))
        return {"editor_actions": list(editor_actions)}


@api.route(f'{MANUSCRIPT_EP}/referee_actions')
class ManuscriptRefereeActions(Resource):
    """
    This class handles getting all possible referee actions.
    """
    def get(self):
        """
        Get all possible referee actions.
        """
        # Referee actions are those that can be taken in IN_REF_REV state
        referee_actions = set(ms.get_valid_actions_by_state(ms.IN_REF_REV))
        return {"referee_actions": list(referee_actions)}


@api.route(f'{DEV_EP}/editor_dashboard')
class EditorDashboardPermission(Resource):
    @sec.requires_permission('editor_dashboard', 'access', roles=['ED', 'ME'])
    def get(self):
        return {'message': 'Authorized'}, HTTPStatus.OK


@api.route('/dev/clear_db')
class ClearDatabase(Resource):
    """
    WARNING: Development-only endpoint. Drops the entire journal database.
    """
    def delete(self):
        from data.db_connect import connect_db, JOURNAL_DB
        client = connect_db()
        client.drop_database(JOURNAL_DB)
        return {'message': f"Database '{JOURNAL_DB}' dropped."}, HTTPStatus.OK
