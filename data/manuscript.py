import data.db_connect as dbc


# Fields (originally fields.py)
TITLE = 'title'
AUTHOR = 'author'
REFEREES = 'referees'
STATE = 'state'
DISP_NAME = 'disp_name'


FIELDS = {
    TITLE: {
        DISP_NAME: 'Title',
    },
    AUTHOR: {
        DISP_NAME: 'Author',
    },
    REFEREES: {
        DISP_NAME: 'Referees',
    },
    STATE: {
        DISP_NAME: 'State',
    },
}


def get_flds() -> dict:
    return FIELDS


def get_fld_names() -> list:
    return list(FIELDS.keys())


def get_disp_name(fld_nm: str) -> str:
    fld = FIELDS.get(fld_nm, '')
    return fld[DISP_NAME] if fld else ''


# Form handling (originally form_filler.py and form.py)
FLD_NM = 'fld_nm'
QSTN = 'question'
PARAM_TYPE = 'param_type'
QUERY_STR = 'query_string'
LIST = 'list'
DEFAULT = 'default'
OPT = 'optional'
CHOICES = 'choices'
TYPECAST = 'typecast'
INT = 'int'


def get_input(dflt, opt, qstn):
    """
    Helper for user input. In production
    this might be adapted or replaced with mocks or a GUI.
    """
    return input(f'{dflt}{opt}{qstn} ')


def form(fld_descrips):
    print('For optional fields just hit Enter if you do not want a value.')
    print('For fields with a default just hit Enter if you want the default.')
    fld_vals = {}
    for fld in fld_descrips:
        opt = ''
        dflt = ''
        if CHOICES in fld:
            print(f'Options: {fld[CHOICES]}')
        if OPT in fld:
            opt = '(OPTIONAL) '
        if DEFAULT in fld:
            dflt = f'(DEFAULT: {fld["default"]}) '
        if QSTN in fld:
            val = get_input(dflt, opt, fld[QSTN])
            if TYPECAST in fld and fld[TYPECAST] == INT and val.strip():
                val = int(val)
            # If empty and default available:
            if not val.strip() and DEFAULT in fld:
                val = fld[DEFAULT]
            fld_vals[fld[FLD_NM]] = val
        else:
            fld_vals[fld[FLD_NM]] = ''
    return fld_vals


# Manuscript form fields
MANUSCRIPT_FORM = [
    {
        FLD_NM: TITLE,
        QSTN: 'Title:',
        PARAM_TYPE: QUERY_STR,
    },
    {
        FLD_NM: AUTHOR,
        QSTN: 'Author:',
        PARAM_TYPE: QUERY_STR,
    },
    {
        FLD_NM: REFEREES,
        QSTN: 'Referees (comma separated):',
        PARAM_TYPE: LIST,
    },
]


def get_form_descr(fld_descrips: list) -> dict:
    descr = {}
    for fld in fld_descrips:
        if fld.get(PARAM_TYPE, '') == QUERY_STR:
            fld_nm = fld[FLD_NM]
            descr[fld_nm] = fld[QSTN]
            if CHOICES in fld:
                descr[fld_nm] += f'\nChoices: {fld[CHOICES]}'
    return descr


def get_form() -> list:
    return MANUSCRIPT_FORM


def get_form_field_names() -> list:
    return [f[FLD_NM] for f in MANUSCRIPT_FORM]


# States and Actions (originally query.py)
AUTHOR_REV = 'AUR'
COPY_EDIT = 'CED'
IN_REF_REV = 'REV'
REJECTED = 'REJ'
SUBMITTED = 'SUB'
WITHDRAWN = 'WIT'    #
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
    WITHDRAWN,      #
]


def get_states() -> list:
    return VALID_STATES


def is_valid_state(state: str) -> bool:
    return state in VALID_STATES


# Actions
ACCEPT = 'ACC'
ASSIGN_REF = 'ARF'
DELETE_REF = 'DRF'  #
DONE = 'DON'
REJECT = 'REJ'
WITHDRAW = 'WIT'    #
REMOVE_REF = 'RRF'
SUBMIT_REVIEW = 'SBR'
ACCEPT_WITH_REVISIONS = 'AWR'


TEST_ACTION = ACCEPT


VALID_ACTIONS = [
    ACCEPT,
    ASSIGN_REF,
    DELETE_REF,     #
    DONE,
    REJECT,
    REMOVE_REF,
    SUBMIT_REVIEW,
    WITHDRAW,
    ACCEPT_WITH_REVISIONS,
]


def get_actions() -> list:
    return VALID_ACTIONS


def is_valid_action(action: str) -> bool:
    return action in VALID_ACTIONS


FUNC = 'f'


# We will define helper functions for actions:
def assign_ref(manu: dict, **kwargs) -> str:
    ref = kwargs.get('ref')
    if not ref:
        raise ValueError("Assign_ref action requires a 'ref' parameter.")
    manu[REFEREES].append(ref)
    return IN_REF_REV


def delete_ref(manu: dict, **kwargs) -> str:
    ref = kwargs.get('ref')
    if not ref:
        raise ValueError("Delete_ref action requires a 'ref' parameter.")
    # Attempt to remove the ref if present:
    if ref in manu[REFEREES]:
        manu[REFEREES].remove(ref)
    # Decide next state based on remaining referees:
    return IN_REF_REV if manu[REFEREES] else SUBMITTED


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
        REMOVE_REF: {
            FUNC: lambda **kwargs: SUBMITTED,
        },
        SUBMIT_REVIEW: {
            FUNC: lambda **kwargs: IN_REF_REV,
        },
        **COMMON_ACTIONS,
    },
    COPY_EDIT: {
        DONE: {
            FUNC: lambda **kwargs: AUTHOR_REV,  #
        },
        **COMMON_ACTIONS,  #
    },
    AUTHOR_REV: {
        **COMMON_ACTIONS,  #
    },
    EDITOR_REV: {
        ACCEPT: {
            FUNC: lambda **kwargs: COPY_EDIT,
        },
    },
    FORMATTING: {
        DONE: {
            FUNC: lambda **kwargs: PUBLISHED,
        },
    },
    PUBLISHED: {},
    REJECTED: {
        **COMMON_ACTIONS,
    },
    WITHDRAWN: {
        **COMMON_ACTIONS,
    },
}


def handle_action(
    curr_state: str,
    action: str,
    manu: dict,
    ref: str = None
) -> str:
    """
    Determine the new manuscript state given the current state and action.
    Uses the STATE_TABLE to find the correct transition.
    """
    if not is_valid_state(curr_state):
        raise ValueError(f"Invalid current state: {curr_state}")
    if not is_valid_action(action):
        raise ValueError(f"Invalid action: {action}")

    if curr_state not in STATE_TABLE:
        raise ValueError(f"Bad state: {curr_state}")
    if action not in STATE_TABLE[curr_state]:
        raise ValueError(f"{action} not available in {curr_state}")

    action_entry = STATE_TABLE[curr_state][action]
    action_func = action_entry[FUNC]
    new_state = action_func(manu=manu, ref=ref)
    if not is_valid_state(new_state):
        raise ValueError(f"handle_action returned invalid state: {new_state}")
    return new_state


# Database and CRUD
MANUSCRIPTS_COLLECT = 'manuscripts'


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


def create(title: str, author: str):
    """
    Create a new manuscript with the given title and author.
    Raises ValueError if title or author is blank,
    or if manuscript already exists.
    """
    if not title.strip():
        raise ValueError("Title cannot be blank")
    if not author.strip():
        raise ValueError("Author cannot be blank")
    if exists(title):
        raise ValueError(f"Manuscript with {title=} already exists.")
    manuscript = {
        TITLE: title,
        AUTHOR: author,
        REFEREES: [],
        STATE: SUBMITTED,
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


def update(
    title: str,
    author: str = None,
    referees: list = None,
    state: str = None
):
    """
    Update the specified fields of the manuscript identified by title.
    You can update author, referees, and state if provided.
    """
    manu = read_one(title)
    if not manu:
        raise ValueError(f'Updating non-existent manuscript: {title=}')
    updated_fields = {}
    if author is not None:
        if not author.strip():
            raise ValueError("Author can't be blank.")
        updated_fields[AUTHOR] = author
    if referees is not None:
        updated_fields[REFEREES] = referees
    if state is not None:
        if not is_valid_state(state):
            raise ValueError(f"Invalid state: {state}")
        updated_fields[STATE] = state
    if updated_fields:
        dbc.update(MANUSCRIPTS_COLLECT, {TITLE: title}, updated_fields)
    return title


def add_referee(title: str, referee: str):
    if not referee or not referee.strip():
        raise ValueError("Referee name cannot be blank or empty.")
    manu = read_one(title)
    if not manu:
        raise ValueError(f"No manuscript with title={title}")
    if referee in manu[REFEREES]:
        raise ValueError(
            f"Referee {referee} already exists for manuscript {title}."
        )

    manu[REFEREES].append(referee)
    update(title, referees=manu[REFEREES])
    return title


def remove_referee(title: str, referee: str):
    if not referee or not referee.strip():
        raise ValueError("Referee name cannot be blank or empty.")
    manu = read_one(title)
    if not manu:
        raise ValueError(f"No manuscript with title={title}")
    if referee not in manu[REFEREES]:
        raise ValueError(
            f"Referee {referee} does not exist for manuscript {title}."
        )
    manu[REFEREES].remove(referee)
    update(title, referees=manu[REFEREES])
    return title


def handle_action_on_manuscript(title: str, action: str, referee: str = None):
    manu = read_one(title)
    if not manu:
        raise ValueError(f"No manuscript found with title={title}")
    current_state = manu[STATE]

    # Validate state and action before proceeding
    if not is_valid_state(current_state):
        raise ValueError(f"Invalid state encountered: {current_state}")
    if not is_valid_action(action):
        raise ValueError(f"Invalid action: {action}")
    # Proceed with the action
    new_state = handle_action(current_state, action, manu=manu, ref=referee)
    # Validate the returned state
    if not is_valid_state(new_state):
        raise ValueError(f"handle_action returned invalid state: {new_state}")
    # Update manuscript with new state and referees
    update(title, referees=manu[REFEREES], state=new_state)
    return new_state


def main():
    pass


if __name__ == '__main__':
    main()
