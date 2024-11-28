"""
This module interfaces to our user data.
"""

# fields
PAGE_NUMBER = 'pageNumber'
TITLE = 'title'
TEXT = 'text'

TEST_PAGE_NUMBER = 'HomePage'
SUBM_PAGE_NUMBER = 'SubmissionsPage'
DEL_PAGE_NUMBER = 'DeletePage'

text_dict = {
    TEST_PAGE_NUMBER: {
        TITLE: 'Home Page',
        TEXT: 'This is a journal about building API servers.',
    },
    SUBM_PAGE_NUMBER: {
        TITLE: 'Submissions Page',
        TEXT: 'All submissions must be original work in Word format.',
    },
    DEL_PAGE_NUMBER: {
        TITLE: 'Delete Page',
        TEXT: 'This is a text to delete.',
    },
}


def read():
    """
    Our contract:
        - No arguments.
        - Returns a dictionary of users page_number on user email.
        - Each user email must be the page_number for another dictionary.
    """
    text = text_dict
    return text


def read_one(page_number: str) -> dict:
    # This should take a page number and return the page dictionary
    # for that page number. Return an empty dictionary of number not found.
    result = {}
    if page_number in text_dict:
        result = text_dict[page_number]
    return result


def delete(page_number: str):
    """
    Deletes a page entry from the text dictionary.
    """
    texts = read()
    if page_number in texts:
        del texts[page_number]
        return page_number
    else:
        return None


def create(page_number: str, title: str, text: str):
    if page_number in text_dict:
        raise ValueError(f'Adding duplicate {page_number=}')
    if not title.strip() or not text.strip():
        raise ValueError('Title or text can not be blank')
    text_dict[page_number] = {TITLE: title, TEXT: text}
    return page_number


def update(page_number: str, field: str, value: str):
    if not value.strip():
        raise ValueError("Value can't be blank")
    if page_number not in text_dict:
        raise ValueError(f'{page_number} do not exist')
    if field != TITLE and field != TEXT:
        raise ValueError(f'{field} is not a valid field to update')
    text_dict[page_number][field] = value
    return page_number
