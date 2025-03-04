"""
This module interfaces to our text data for manuscripts.
Each manuscript can have multiple text pages, each with a page number, title, and content.
"""

import data.db_connect as dbc

TEXT_COLLECT = 'texts'

# fields
MANUSCRIPT_ID = 'manuscript_id'  # Reference to the manuscript this text belongs to
PAGE_NUMBER = 'pageNumber'
TITLE = 'title'
TEXT = 'text'

client = dbc.connect_db()
print(f'{client=}')


def read():
    """
    Our contract:
        - No arguments.
        - Returns a dictionary of texts keyed on page number.
    """
    text = dbc.read_dict(TEXT_COLLECT, PAGE_NUMBER)
    return text


def read_by_manuscript(manuscript_id: str) -> list:
    """
    Get all text pages for a specific manuscript.
    
    Args:
        manuscript_id: The ID of the manuscript
        
    Returns:
        A list of text pages for the manuscript, sorted by page number
    """
    texts = dbc.read_many(TEXT_COLLECT, {MANUSCRIPT_ID: manuscript_id})
    # Sort by page number
    return sorted(texts, key=lambda x: x[PAGE_NUMBER])


def read_one(page_number: str, manuscript_id: str = None) -> dict:
    """
    Read a single text page by page number.
    If manuscript_id is provided, read the text page for that manuscript.
    
    Args:
        page_number: The page number to read
        manuscript_id: Optional. The manuscript ID to read
        
    Returns:
        The text page dictionary, or None if not found
    """
    if manuscript_id:
        return dbc.read_one(TEXT_COLLECT, {PAGE_NUMBER: page_number, MANUSCRIPT_ID: manuscript_id})
    else:
        return dbc.read_one(TEXT_COLLECT, {PAGE_NUMBER: page_number})


def exists(page_number: str, manuscript_id: str = None) -> bool:
    """
    Check if a text page with the given page number exists.
    If manuscript_id is provided, check if a text page with the given page number exists for that manuscript.
    
    Args:
        page_number: The page number to check
        manuscript_id: Optional. The manuscript ID to check
        
    Returns:
        True if the page exists, False otherwise
    """
    if manuscript_id:
        return dbc.read_one(TEXT_COLLECT, {PAGE_NUMBER: page_number, MANUSCRIPT_ID: manuscript_id}) is not None
    else:
        return dbc.read_one(TEXT_COLLECT, {PAGE_NUMBER: page_number}) is not None


def is_valid_text(manuscript_id: str, page_number: str, title: str, text: str):
    print(f"Validating text: {manuscript_id=}, {page_number=}, {title=}")
    print(f"Text length: {len(text) if text else 0}")
    
    if not manuscript_id.strip():
        print("Manuscript ID is blank")
        raise ValueError('Manuscript ID cannot be blank')
    if not page_number.strip():
        print("Page number is blank")
        raise ValueError('Page number cannot be blank')
    if not title.strip():
        print("Title is blank")
        raise ValueError('Title cannot be blank')
    if not text.strip():
        print("Text is blank")
        raise ValueError('Text cannot be blank')
    
    print("Text validation successful")
    return True


def delete(page_number: str):
    del_num = dbc.delete(TEXT_COLLECT, {PAGE_NUMBER: page_number})
    return page_number if del_num == 1 else None


def delete_manuscript_texts(manuscript_id: str):
    """
    Delete all text pages associated with a manuscript.
    
    Args:
        manuscript_id: The ID of the manuscript
        
    Returns:
        The number of deleted text pages
    """
    result = dbc.delete_many(TEXT_COLLECT, {MANUSCRIPT_ID: manuscript_id})
    return result.deleted_count


def create(manuscript_id: str, page_number: str, title: str, text: str):
    """
    Create a new text page for a manuscript.
    
    Args:
        manuscript_id: The ID of the manuscript this text belongs to
        page_number: The page number
        title: The title of the text
        text: The content of the text
        
    Returns:
        The page number if creation succeeded
    """
    if exists(page_number, manuscript_id):
        raise ValueError(f'Adding duplicate page_number={page_number} for manuscript_id={manuscript_id}')
    if is_valid_text(manuscript_id, page_number, title, text):
        new_text = {
            MANUSCRIPT_ID: manuscript_id,
            PAGE_NUMBER: page_number, 
            TITLE: title, 
            TEXT: text
        }
        dbc.create(TEXT_COLLECT, new_text)
        return page_number


def update(manuscript_id: str, page_number: str, title: str, text: str):
    """
    Update an existing text page.
    
    Args:
        manuscript_id: The ID of the manuscript this text belongs to
        page_number: The page number
        title: The title of the text
        text: The content of the text
        
    Returns:
        The page number if update succeeded
    """
    print(f"Updating text page: {manuscript_id=}, {page_number=}, {title=}")
    print(f"Text length: {len(text) if text else 0}")
    
    if not exists(page_number, manuscript_id):
        print(f"Page does not exist: {page_number=}, {manuscript_id=}")
        raise ValueError(f'Updating non-existent page: page_number={page_number} for manuscript_id={manuscript_id}')
    
    try:
        print("Validating text data")
        if is_valid_text(manuscript_id, page_number, title, text):
            print("Text validation successful, updating in database")
            dbc.update(TEXT_COLLECT, {PAGE_NUMBER: page_number, MANUSCRIPT_ID: manuscript_id},
                   {TITLE: title, TEXT: text})
            print(f"Successfully updated text page {page_number} for manuscript {manuscript_id}")
            return page_number
    except Exception as e:
        print(f"Error in text.update: {str(e)}")
        raise
