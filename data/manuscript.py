import data.db_connect as dbc
import data.people as ppl
from bson import ObjectId

MANUSCRIPTS_COLLECT = 'manuscripts'

# Fields
MANU_ID = '_id'
TITLE = 'title'
AUTHOR = 'author'
AUTHOR_EMAIL = 'author_email'
STATE = 'state'
REFEREES = 'referees'
TEXT = 'text'
ABSTRACT = 'abstract'
HISTORY = 'history'
EDITOR_EMAIL = 'editor_email'


# States
AUTHOR_REV = 'AUR'
COPY_EDIT = 'CED'
IN_REF_REV = 'REV'
REJECTED = 'REJ'
SUBMITTED = 'SUB'
WITHDRAWN = 'WIT'
EDITOR_REV = 'EDR'
AUTHOR_REVISION = 'ARV'
FORMATTING = 'FMT'
PUBLISHED = 'PUB'
TEST_STATE = SUBMITTED


VALID_STATES = [
    AUTHOR_REV,
    COPY_EDIT,
    IN_REF_REV,
    REJECTED,
    SUBMITTED,
    EDITOR_REV,
    AUTHOR_REVISION,
    FORMATTING,
    PUBLISHED,
    WITHDRAWN,
]


def get_states() -> list:
    return VALID_STATES


def is_valid_state(state: str) -> bool:
    return state in VALID_STATES


# Actions
ACCEPT = 'ACC'
ASSIGN_REF = 'ARF'
DELETE_REF = 'DRF'
DONE = 'DON'
REJECT = 'REJ'
WITHDRAW = 'WIT'
SUBMIT_REVIEW = 'SBR'
ACCEPT_WITH_REVISIONS = 'AWR'
TEST_ACTION = ACCEPT


VALID_ACTIONS = [
    ACCEPT,
    ASSIGN_REF,
    DELETE_REF,
    DONE,
    REJECT,
    SUBMIT_REVIEW,
    WITHDRAW,
    ACCEPT_WITH_REVISIONS,
]


def get_actions() -> list:
    return VALID_ACTIONS


def is_valid_action(action: str) -> bool:
    return action in VALID_ACTIONS


def to_object_id(manu_id):
    """
    Convert a string to an Mongo ObjectId if valid, otherwise return None.
    """
    try:
        return ObjectId(manu_id)
    except Exception:
        return None


def assign_ref(manu_id: str, ref: str, extra=None) -> str:
    manuscript = read_one(manu_id)
    if not manuscript:
        raise ValueError(f"Manuscript with _id '{manu_id}' not found")
    if not ref.strip():
        raise ValueError("Name of this referee can't be empty")
    referees = manuscript[REFEREES]
    if ref not in referees:
        referees.append(ref)
    else:
        raise ValueError(f"Referee '{ref}' is already",
                         "assigned to '{manuscript[TITLE]}'.")
    dbc.update(MANUSCRIPTS_COLLECT, {MANU_ID: to_object_id(manu_id)},
               {REFEREES: referees})
    return IN_REF_REV


def delete_ref(manu_id: str, ref: str) -> str:
    manuscript = read_one(manu_id)
    if not manuscript:
        raise ValueError(f"Manuscript with _id '{manu_id}' not found")
    if not ref.strip():
        raise ValueError("Name of this referee can't be empty")
    referees = manuscript[REFEREES]
    if ref not in referees:
        raise ValueError(f"This referee '{ref}' is not reviewing the journal")
    referees.remove(ref)
    dbc.update(MANUSCRIPTS_COLLECT, {MANU_ID: to_object_id(manu_id)},
               {REFEREES: referees})
    if len(referees) > 0:
        return IN_REF_REV
    else:
        return SUBMITTED


FUNC = 'f'

COMMON_ACTIONS = {
    WITHDRAW: {
        FUNC: lambda **kwargs: WITHDRAWN,
    },
}


# STATE_TABLE: A dictionary mapping current_state ->
# {action: function(manu, ref, **kwargs) -> new_state}
STATE_TABLE = {
    SUBMITTED: {
        ASSIGN_REF: {
            FUNC: assign_ref,
        },
        REJECT: {
            FUNC: lambda **kwargs: REJECTED,
        },
        **COMMON_ACTIONS,
    },
    IN_REF_REV: {
        ASSIGN_REF: {
            FUNC: assign_ref,
        },
        DELETE_REF: {
            FUNC: delete_ref,
        },
        ACCEPT: {
            FUNC: lambda **kwargs: COPY_EDIT,
        },
        REJECT: {
            FUNC: lambda **kwargs: REJECTED,
        },
        ACCEPT_WITH_REVISIONS: {
            FUNC: lambda **kwargs: AUTHOR_REVISION,
        },
        SUBMIT_REVIEW: {
            FUNC: lambda **kwargs: IN_REF_REV,
        },
        **COMMON_ACTIONS,
    },
    COPY_EDIT: {
        DONE: {
            FUNC: lambda **kwargs: AUTHOR_REV,
        },
        **COMMON_ACTIONS,
    },
    AUTHOR_REV: {
        DONE: {
            FUNC: lambda **kwargs: FORMATTING,
        },
        **COMMON_ACTIONS,
    },
    AUTHOR_REVISION: {
        DONE: {
            FUNC: lambda **kwargs: EDITOR_REV,
        },
        **COMMON_ACTIONS,
    },
    EDITOR_REV: {
        ACCEPT: {
            FUNC: lambda **kwargs: COPY_EDIT,
        },
        **COMMON_ACTIONS,
    },
    FORMATTING: {
        DONE: {
            FUNC: lambda **kwargs: PUBLISHED,
        },
        **COMMON_ACTIONS,
    },
    PUBLISHED: {
        **COMMON_ACTIONS,
    },
    REJECTED: {
        **COMMON_ACTIONS,
    },
    WITHDRAWN: {},
}


def get_valid_actions_by_state(state: str):
    valid_actions = STATE_TABLE[state].keys()
    print(f'{valid_actions=}')
    return valid_actions


def handle_action(manu_id, curr_state, action, **kwargs) -> str:
    kwargs['manu_id'] = manu_id
    if curr_state not in STATE_TABLE:
        raise ValueError(f'Bad state: {curr_state}')
    if action not in STATE_TABLE[curr_state]:
        raise ValueError(f'{action} not available in {curr_state}')
    return STATE_TABLE[curr_state][action][FUNC](**kwargs)


def read() -> dict:
    """
    Return a dictionary of all manuscripts keyed by their title.
    """
    manuscripts = dbc.read_dict(MANUSCRIPTS_COLLECT, TITLE, no_id=False)
    return manuscripts


def read_one(manu_id: str) -> dict:
    """
    Return a single manuscript record as a dict, or None if not found.
    """
    return dbc.read_one(MANUSCRIPTS_COLLECT, {MANU_ID: to_object_id(manu_id)})


def exists(manu_id: str) -> bool:
    """
    Check if a manuscript with the given manu_id exists in the database.
    """
    return read_one(manu_id) is not None


def is_valid_manuscript(title: str, author: str,
                        author_email: str, text: str,
                        abstract: str, editor_email: str) -> bool:
    if not ppl.is_valid_email(author_email):
        raise ValueError(f'Author email invalid: {author_email}')
    if not ppl.is_valid_email(editor_email):
        raise ValueError(f'Editor email invalid: {editor_email}')
    if not title.strip():
        raise ValueError("Title cannot be blank")
    if not author.strip():
        raise ValueError("Author cannot be blank")
    if not text.strip():
        raise ValueError("Text cannot be blank")
    if not abstract.strip():
        raise ValueError("Abstract cannot be blank")
    return True


def create(title: str, author: str, author_email: str,
           text: str, abstract: str, editor_email: str):
    if is_valid_manuscript(title, author, author_email, text,
                           abstract, editor_email):
        manuscript = {
            TITLE: title,
            AUTHOR: author,
            AUTHOR_EMAIL: author_email,
            STATE: SUBMITTED,
            REFEREES: [],
            TEXT: text,
            ABSTRACT: abstract,
            HISTORY: [SUBMITTED],
            EDITOR_EMAIL: editor_email,
        }
        result = dbc.create(MANUSCRIPTS_COLLECT, manuscript)
        return str(result.inserted_id)


def delete(manu_id: str):
    """
    Delete the manuscript with the given manu_id.
    Returns the manu_id if deletion succeeded, else None.
    """
    del_num = dbc.delete(MANUSCRIPTS_COLLECT, {MANU_ID: to_object_id(manu_id)})
    return manu_id if del_num == 1 else None


def update(manu_id: str, title: str, author: str, author_email: str,
           text: str, abstract: str, editor_email: str):
    if not exists(manu_id):
        raise ValueError(f'Updating non-existent manuscript: {manu_id=}')
    if is_valid_manuscript(title, author, author_email, text,
                           abstract, editor_email):
        updated_fields = {
            TITLE: title,
            AUTHOR: author,
            AUTHOR_EMAIL: author_email,
            TEXT: text,
            ABSTRACT: abstract,
            EDITOR_EMAIL: editor_email,
        }
        dbc.update(MANUSCRIPTS_COLLECT,
                   {MANU_ID: to_object_id(manu_id)},
                   updated_fields)
        return manu_id


def update_state(manu_id: str, action: str, **kwargs):
    """
    Updates the state of a manuscript based on the given action.
    :param manu_id: The _id of the manuscript to update.
    :param action: The action to perform (e.g., ACCEPT, REJECT, ASSIGN_REF).
    :param kwargs: Additional arguments required by specific actions.
    :return: The updated state of the manuscript.
    """
    manuscript = read_one(manu_id)
    current_state = manuscript[STATE]
    # Determine the new state using handle_action
    new_state = handle_action(
        manu_id, current_state, action, **kwargs
    )
    # Update the manuscript state and history in the database
    dbc.update(
        MANUSCRIPTS_COLLECT,
        {MANU_ID: to_object_id(manu_id)},
        {
            STATE: new_state,
            HISTORY: manuscript[HISTORY] + [new_state],
        },
    )
    return manu_id


def main():
    pass


if __name__ == '__main__':
    main()
