import data.db_connect as dbc
import data.people as ppl

MANUSCRIPTS_COLLECT = 'manuscripts'

# Fields
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


def assign_ref(title: str, ref: str, extra=None) -> str:
    print(extra)
    manuscripts = read_one(title)
    if not manuscripts:
        raise ValueError(f"Manuscript with title '{title}' not found")
    if not ref.strip():
        raise ValueError("Name of this referee can't be empty")
    referees = manuscripts[REFEREES]
    if ref not in referees:
        referees.append(ref)
    else:
        raise ValueError(f"Referee '{ref}' is already assigned to '{title}'.")
    dbc.update(MANUSCRIPTS_COLLECT, {TITLE: title},
               {REFEREES: referees})
    return IN_REF_REV


def delete_ref(title: str, ref: str) -> str:
    manuscripts = read_one(title)
    if not manuscripts:
        raise ValueError(f"Manuscript with title '{title}' not found")
    if not ref.strip():
        raise ValueError("Name of this referee can't be empty")
    referees = manuscripts[REFEREES]
    if ref not in referees:
        raise ValueError(f"This referee '{ref}' is not reviewing the journal")
    referees.remove(ref)
    dbc.update(MANUSCRIPTS_COLLECT, {TITLE: title},
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


def handle_action(curr_state, action, **kwargs) -> str:
    if curr_state not in STATE_TABLE:
        raise ValueError(f'Bad state: {curr_state}')
    if action not in STATE_TABLE[curr_state]:
        raise ValueError(f'{action} not available in {curr_state}')
    return STATE_TABLE[curr_state][action][FUNC](**kwargs)


def read() -> dict:
    """
    Return a dictionary of all manuscripts keyed by their title.
    """
    manuscripts = dbc.read_dict(MANUSCRIPTS_COLLECT, TITLE)
    return manuscripts


def read_one(title: str) -> dict:
    """
    Return a single manuscript record as a dict, or None if not found.
    """
    return dbc.read_one(MANUSCRIPTS_COLLECT, {TITLE: title})


def exists(title: str) -> bool:
    """
    Check if a manuscript with the given title exists in the database.
    """
    return read_one(title) is not None


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
    if exists(title):
        raise ValueError(f"Manuscript with {title=} already exists.")
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
        dbc.create(MANUSCRIPTS_COLLECT, manuscript)
        return title


def delete(title: str):
    """
    Delete the manuscript with the given title.
    Returns the title if deletion succeeded, else None.
    """
    del_num = dbc.delete(MANUSCRIPTS_COLLECT, {TITLE: title})
    return title if del_num == 1 else None


def update(title: str, author: str, author_email: str,
           text: str, abstract: str, editor_email: str):
    if not exists(title):
        raise ValueError(f'Updating non-existent manuscript: {title=}')
    if is_valid_manuscript(title, author, author_email, text,
                           abstract, editor_email):
        updated_fields = {
            AUTHOR: author,
            AUTHOR_EMAIL: author_email,
            TEXT: text,
            ABSTRACT: abstract,
            EDITOR_EMAIL: editor_email,
        }
        dbc.update(MANUSCRIPTS_COLLECT, {TITLE: title}, updated_fields)
        return title


def update_state(title: str, action: str, **kwargs):
    """
    Updates the state of a manuscript based on the given action.
    :param title: The title of the manuscript to update.
    :param action: The action to perform (e.g., ACCEPT, REJECT, ASSIGN_REF).
    :param kwargs: Additional arguments required by specific actions.
    :return: The updated state of the manuscript.
    """
    manuscript = read_one(title)
    current_state = manuscript[STATE]
    # Determine the new state using handle_action
    new_state = handle_action(
        current_state, action, title=title, **kwargs
    )
    # Update the manuscript state and history in the database
    dbc.update(
        MANUSCRIPTS_COLLECT,
        {TITLE: title},
        {
            STATE: new_state,
            HISTORY: manuscript[HISTORY] + [new_state],
        },
    )
    return title


def main():
    pass


if __name__ == '__main__':
    main()
