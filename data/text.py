"""
This module interfaces to our user data.
"""

import data.db_connect as dbc

TEXT_COLLECT = 'texts'

# fields
PAGE_NUMBER = 'pageNumber'
TITLE = 'title'
TEXT = 'text'

client = dbc.connect_db()
print(f'{client=}')


def read():
    """
    Our contract:
        - No arguments.
        - Returns a dictionary of users page_number on user email.
        - Each user email must be the page_number for another dictionary.
    """
    text = dbc.read_dict(TEXT_COLLECT, PAGE_NUMBER)
    return text


def read_one(page_number: str) -> dict:
    # This should take a page number and return the page dictionary
    # for that page number. Return an empty dictionary of number not found.
    return dbc.read_one(TEXT_COLLECT, {PAGE_NUMBER: page_number})


def delete(page_number: str):
    """
    Deletes a page entry from the text dictionary.
    """
    texts = read()
    if page_number in texts:
        del_num = dbc.delete(TEXT_COLLECT, {PAGE_NUMBER: page_number})
        return page_number if del_num == 1 else None
    else:
        return None


def create(page_number: str, title: str, text: str):
    texts = read()
    if page_number in texts:
        raise ValueError(f'Adding duplicate {page_number=}')
    if not title.strip() or not text.strip():
        raise ValueError('Title or text can not be blank')
    new_text = {TITLE: title, TEXT: text, PAGE_NUMBER: page_number}
    dbc.create(TEXT_COLLECT, new_text)
    return page_number


def update(page_number: str, field: str, value: str):
    texts = read()
    if not value.strip():
        raise ValueError("Value can't be blank")
    if page_number not in texts:
        raise ValueError(f'{page_number} do not exist')
    if field == TITLE:
        dbc.update(TEXT_COLLECT, {PAGE_NUMBER: page_number}, {TITLE: value})
    elif field == TEXT:
        dbc.update(TEXT_COLLECT, {PAGE_NUMBER: page_number}, {TEXT: value})
    else:
        raise ValueError(f'{field} is not a valid field to update')
    return page_number
