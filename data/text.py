"""
This module interfaces to our user data.
"""

# fields
KEY = 'key'
TITLE = 'title'
TEXT = 'text'
EMAIL = 'email'

TEST_KEY = 'HomePage'
SUBM_KEY = 'SubmissionsPage'
DEL_KEY = 'DeletePage'

text_dict = {
    TEST_KEY: {
        TITLE: 'Home Page',
        TEXT: 'This is a journal about building API servers.',
    },
    SUBM_KEY: {
        TITLE: 'Submissions Page',
        TEXT: 'All submissions must be original work in Word format.',
    },
    DEL_KEY: {
        TITLE: 'Delete Page',
        TEXT: 'This is a text to delete.',
    },
}


def read():
    """
    Our contract:
        - No arguments.
        - Returns a dictionary of users keyed on user email.
        - Each user email must be the key for another dictionary.
    """
    text = text_dict
    return text


def read_one(key: str) -> dict:
    # This should take a key and return the page dictionary
    # for that key. Return an empty dictionary of key not found.
    result = {}
    if key in text_dict:
        result = text_dict[key]
    return result


def delete(key: str):
    """
    Deletes a page entry from the text dictionary.
    """
    texts = read()
    if key in texts:
        del texts[key]
        return key
    else:
        return None


def create(key: str, title: str, text: str):
    if key in text_dict:
        raise ValueError(f'Adding duplicate {key=}')
    text_dict[key] = {TITLE: title, TEXT: text}
    return key
