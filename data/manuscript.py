import data.db_connect as dbc
import data.people as ppl
import data.text as text_module
from bson import ObjectId

MANUSCRIPTS_COLLECT = 'manuscripts'

# Fields
MANU_ID = '_id'
TITLE = 'title'
AUTHOR = 'author'
AUTHOR_EMAIL = 'author_email'
STATE = 'state'
REFEREES = 'referees'
# TEXT field is deprecated - we now use the text collection
# but keeping it for backward compatibility with endpoints.py
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
    if not manu_id:
        print("Cannot convert empty or None manuscript ID to ObjectId")
        return None
        
    try:
        print(f"Converting manu_id to ObjectId: {manu_id}")
        obj_id = ObjectId(manu_id)
        print(f"Successfully converted to ObjectId: {obj_id}")
        return obj_id
    except Exception as e:
        print(f"Failed to convert manu_id to ObjectId: {manu_id}, error: {str(e)}")
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


def read() -> list:
    """
    Our contract:
        - No arguments.
        - Returns a list of all manuscripts.
    """
    manuscripts = dbc.read_dict(MANUSCRIPTS_COLLECT, TITLE, no_id=False)
    # Convert the dictionary to a list of manuscripts
    return list(manuscripts.values()) if manuscripts else []


def read_one(manu_id: str) -> dict:
    """
    Return a single manuscript record as a dict, or None if not found.
    """
    print(f"Reading manuscript with ID: {manu_id}")
    obj_id = to_object_id(manu_id)
    if obj_id is None:
        print(f"Invalid manuscript ID format: {manu_id}")
        return None
    
    manuscript = dbc.read_one(MANUSCRIPTS_COLLECT, {MANU_ID: obj_id})
    if manuscript:
        print(f"Found manuscript: {manuscript}")
    else:
        print(f"No manuscript found with ID: {manu_id}")
    
    return manuscript


def exists(manu_id: str) -> bool:
    """
    Check if a manuscript with the given manu_id exists in the database.
    """
    if not manu_id:
        print("Cannot check existence of empty or None manuscript ID")
        return False
        
    print(f"Checking if manuscript exists: {manu_id}")
    manuscript = read_one(manu_id)
    exists = manuscript is not None
    print(f"Manuscript exists: {exists}")
    return exists


def is_valid_manuscript(title: str, author: str,
                        author_email: str, text: str,
                        abstract: str, editor_email: str,
                        manu_id: str = None) -> bool:
    """
    Validate manuscript data before creation or update.
    
    Note: The text parameter is validated here but will be stored in the text collection,
    not directly in the manuscript document.
    
    Args:
        title: The manuscript title
        author: The author name
        author_email: The author's email
        text: The initial text content (will be stored as page 1)
        abstract: The manuscript abstract
        editor_email: The editor's email
        manu_id: Optional. The manuscript ID when updating an existing manuscript
        
    Returns:
        True if all validations pass
        
    Raises:
        ValueError: If any validation fails
    """
    print(f"Validating manuscript: {title=}, {author=}, {author_email=}, {abstract=}, {editor_email=}, {manu_id=}")
    print(f"Text length: {len(text) if text else 0}")
    
    if not ppl.is_valid_email(author_email):
        print(f"Invalid author email: {author_email}")
        raise ValueError(f'Author email invalid: {author_email}')
    if not ppl.is_valid_email(editor_email):
        print(f"Invalid editor email: {editor_email}")
        raise ValueError(f'Editor email invalid: {editor_email}')
    if not title.strip():
        print("Title is blank")
        raise ValueError("Title cannot be blank")
    if not author.strip():
        print("Author is blank")
        raise ValueError("Author cannot be blank")
    
    # Only check text content for new manuscripts or if explicitly provided for updates
    if manu_id is None or (text and text.strip()):
        if not text.strip():
            print("Text is blank")
            raise ValueError("Text cannot be blank")
    else:
        print("Skipping text validation for existing manuscript update")
    
    if not abstract.strip():
        print("Abstract is blank")
        raise ValueError("Abstract cannot be blank")
    
    # Only check for duplicate manuscripts when creating a new one (manu_id is None)
    if manu_id is None:
        print("Checking for duplicate manuscripts (new manuscript)")
        existing_manuscript = dbc.read_one(MANUSCRIPTS_COLLECT,
                                        {TITLE: title,
                                            AUTHOR_EMAIL: author_email})
        if existing_manuscript:
            print(f"Found duplicate manuscript: {existing_manuscript}")
            raise ValueError(f"A manuscript with title '{title}' and "
                            f"author email '{author_email}' already exists.")
    else:
        print(f"Skipping duplicate check for existing manuscript with ID: {manu_id}")
    
    print("Manuscript validation successful")
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
            ABSTRACT: abstract,
            HISTORY: [SUBMITTED],
            EDITOR_EMAIL: editor_email,
        }
        result = dbc.create(MANUSCRIPTS_COLLECT, manuscript)
        manu_id = str(result.inserted_id)
        
        # Create the first text page for this manuscript
        text_module.create(manu_id, "1", f"Page 1 of {title}", text)
        
        return manu_id


def delete(manu_id: str):
    """
    Delete the manuscript with the given manu_id.
    Returns the manu_id if deletion succeeded, else None.
    """
    # First delete all text pages associated with this manuscript
    text_module.delete_manuscript_texts(manu_id)
    
    # Then delete the manuscript itself
    del_num = dbc.delete(MANUSCRIPTS_COLLECT, {MANU_ID: to_object_id(manu_id)})
    return manu_id if del_num == 1 else None


def update(manu_id: str, title: str, author: str, author_email: str,
           text: str, abstract: str, editor_email: str):
    print(f"Updating manuscript: {manu_id=}, {title=}, {author=}, {author_email=}, {abstract=}, {editor_email=}")
    print(f"Text length: {len(text) if text else 0}")
    print(f"Manuscript ID type: {type(manu_id)}")
    
    # Explicit check for manuscript ID
    if not manu_id:
        print("Manuscript ID is missing or empty")
        raise ValueError('Manuscript ID is required for update')
    
    # Check if manuscript exists
    if not exists(manu_id):
        print(f"Manuscript does not exist: {manu_id=}")
        raise ValueError(f'Updating non-existent manuscript: {manu_id=}')
    
    # Validate manuscript data
    try:
        print(f"Validating manuscript data with manu_id={manu_id}")
        is_valid_manuscript(title, author, author_email, text, abstract, editor_email, manu_id)
        
        # Update manuscript fields
        updated_fields = {
            TITLE: title,
            AUTHOR: author,
            AUTHOR_EMAIL: author_email,
            ABSTRACT: abstract,
            EDITOR_EMAIL: editor_email,
        }
        print(f"Updating manuscript fields: {updated_fields}")
        
        # Convert manu_id to ObjectId
        obj_id = to_object_id(manu_id)
        if not obj_id:
            print(f"Failed to convert manu_id to ObjectId: {manu_id}")
            raise ValueError(f"Invalid manuscript ID format: {manu_id}")
            
        print(f"Using ObjectId for update: {obj_id}")
        dbc.update(MANUSCRIPTS_COLLECT,
                {MANU_ID: obj_id},
                updated_fields)
        
        # Only update text pages if text is provided and not empty
        if text and text.strip():
            try:
                # Update the first text page or create it if it doesn't exist
                text_pages = text_module.read_by_manuscript(manu_id)
                print(f"Found {len(text_pages)} text pages for manuscript {manu_id}")
                
                if text_pages:
                    # Update the first page
                    try:
                        print(f"Attempting to update first text page: {text_pages[0][text_module.PAGE_NUMBER]}")
                        text_module.update(manu_id, text_pages[0][text_module.PAGE_NUMBER], 
                                        f"Page 1 of {title}", text)
                        print("Successfully updated first text page")
                    except ValueError as e:
                        print(f"Error updating first text page: {str(e)}")
                        # If update fails, try to create the page
                        if "Updating non-existent page" in str(e):
                            print("Creating new first page since update failed")
                            text_module.create(manu_id, "1", f"Page 1 of {title}", text)
                        else:
                            raise
                else:
                    # Create a new first page
                    try:
                        print("No text pages found, creating new first page")
                        text_module.create(manu_id, "1", f"Page 1 of {title}", text)
                        print("Successfully created first text page")
                    except ValueError as e:
                        print(f"Error creating first text page: {str(e)}")
                        # If create fails because the page already exists, try to update it
                        if "Adding duplicate page_number" in str(e):
                            print("Updating existing first page since create failed")
                            text_module.update(manu_id, "1", f"Page 1 of {title}", text)
                        else:
                            raise
            except Exception as e:
                print(f"Error handling text pages: {str(e)}")
                # Continue with the update even if text page handling fails
                # We don't want to roll back the manuscript update
                print(f"Manuscript {manu_id} updated, but text page update failed: {str(e)}")
        else:
            print("Skipping text page update as no text content was provided")
        
        print(f"Successfully updated manuscript {manu_id}")
        return manu_id
    except Exception as e:
        print(f"Error in update function: {str(e)}")
        raise


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

# Add new functions to handle text pages

def add_text_page(manu_id: str, page_number: str, title: str, content: str):
    """
    Add a new text page to a manuscript.
    
    Args:
        manu_id: The manuscript ID
        page_number: The page number
        title: The title of the page
        content: The text content
        
    Returns:
        The page number if creation succeeded
    """
    if not exists(manu_id):
        raise ValueError(f'Manuscript does not exist: {manu_id=}')
    
    return text_module.create(manu_id, page_number, title, content)


def get_text_pages(manu_id: str) -> list:
    """
    Get all text pages for a manuscript.
    
    Args:
        manu_id: The manuscript ID
        
    Returns:
        A list of text pages sorted by page number
    """
    if not exists(manu_id):
        raise ValueError(f'Manuscript does not exist: {manu_id=}')
    
    return text_module.read_by_manuscript(manu_id)


def get_text_page(manu_id: str, page_number: str) -> dict:
    """
    Get a specific text page from a manuscript.
    
    Args:
        manu_id: The manuscript ID
        page_number: The page number
        
    Returns:
        The text page dictionary or None if not found
    """
    if not exists(manu_id):
        raise ValueError(f'Manuscript does not exist: {manu_id=}')
    
    page = text_module.read_one(page_number)
    if page and page.get(text_module.MANUSCRIPT_ID) == manu_id:
        return page
    return None


def update_text_page(manu_id: str, page_number: str, title: str, content: str):
    """
    Update a text page in a manuscript.
    
    Args:
        manu_id: The manuscript ID
        page_number: The page number
        title: The new title
        content: The new content
        
    Returns:
        The page number if update succeeded
    """
    if not exists(manu_id):
        raise ValueError(f'Manuscript does not exist: {manu_id=}')
    
    page = text_module.read_one(page_number)
    if not page:
        raise ValueError(f'Page does not exist: {page_number=}')
    
    if page.get(text_module.MANUSCRIPT_ID) != manu_id:
        raise ValueError(f'Page {page_number} does not belong to manuscript {manu_id}')
    
    return text_module.update(manu_id, page_number, title, content)


def delete_text_page(manu_id: str, page_number: str):
    """
    Delete a text page from a manuscript.
    
    Args:
        manu_id: The manuscript ID
        page_number: The page number
        
    Returns:
        The page number if deletion succeeded
    """
    if not exists(manu_id):
        raise ValueError(f'Manuscript does not exist: {manu_id=}')
    
    page = text_module.read_one(page_number)
    if not page:
        return None
    
    if page.get(text_module.MANUSCRIPT_ID) != manu_id:
        raise ValueError(f'Page {page_number} does not belong to manuscript {manu_id}')
    
    return text_module.delete(page_number)
