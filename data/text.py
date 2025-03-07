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


def exists(page_number: str) -> bool:
    return read_one(page_number) is not None


def is_valid_text(page_number: str, title: str, text: str):
    if not page_number.strip():
        raise ValueError('Page number can not be blank')
    if not title.strip():
        raise ValueError('Title can not be blank')
    if not text.strip():
        raise ValueError('Text can not be blank')
    return True


def delete(page_number: str):
    del_num = dbc.delete(TEXT_COLLECT, {PAGE_NUMBER: page_number})
    return page_number if del_num == 1 else None


def create(page_number: str, title: str, text: str):
    if exists(page_number):
        raise ValueError(f'Adding duplicate {page_number=}')
    if is_valid_text(page_number, title, text):
        new_text = {PAGE_NUMBER: page_number, TITLE: title, TEXT: text}
        dbc.create(TEXT_COLLECT, new_text)
        return page_number


def update(page_number: str, title: str, text: str):
    if not exists(page_number):
        raise ValueError(f'Updating non-existent page: {page_number=}')
    if is_valid_text(page_number, title, text):
        dbc.update(TEXT_COLLECT, {PAGE_NUMBER: page_number},
                   {TITLE: title, TEXT: text})
        return page_number
