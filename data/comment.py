import data.db_connect as dbc
import data.manuscript as msc
import data.people as ppl
from bson import ObjectId

COMMENTS_COLLECT = 'comments'
client = dbc.connect_db()

# Fields
COMMENT_ID = '_id'
MANUSCRIPT_ID = 'manuscript_id'
EDITOR_ID = 'editor_id'
TEXT = 'text'
TIMESTAMP = 'timestamp'

def to_object_id(id_str):
    """
    Convert a string to a Mongo ObjectId if valid, otherwise return None.
    """
    try:
        return ObjectId(id_str)
    except Exception:
        return None

def is_valid_comment(manuscript_id: str, editor_id: str, text: str) -> bool:
    """
    Validate a comment before creating or updating it.
    """
    if not manuscript_id or not editor_id or not text:
        raise ValueError("Manuscript ID, editor ID, and text are required.")
    
    if not text.strip():
        raise ValueError("Comment text cannot be empty.")
    
    # Check if manuscript exists
    if not msc.exists(manuscript_id):
        raise ValueError(f"Manuscript with ID '{manuscript_id}' not found.")
    
    # Check if editor exists
    if not ppl.exists(editor_id):
        raise ValueError(f"Editor with ID '{editor_id}' not found.")
    
    return True

def create(manuscript_id: str, editor_id: str, text: str) -> str:
    """
    Create a new comment and return its ID.
    """
    if is_valid_comment(manuscript_id, editor_id, text):
        from datetime import datetime
        
        comment = {
            MANUSCRIPT_ID: manuscript_id,
            EDITOR_ID: editor_id,
            TEXT: text,
            TIMESTAMP: datetime.now()
        }
        
        result = dbc.create(COMMENTS_COLLECT, comment)
        return str(result.inserted_id)

def read_one(comment_id: str) -> dict:
    """
    Return a single comment record as a dict, or None if not found.
    """
    return dbc.read_one(COMMENTS_COLLECT, {COMMENT_ID: to_object_id(comment_id)})

def read_by_manuscript(manuscript_id: str) -> list:
    """
    Return all comments for a specific manuscript.
    """
    comments = []
    for comment in dbc.read(COMMENTS_COLLECT, no_id=False):
        if comment[MANUSCRIPT_ID] == manuscript_id:
            comments.append(comment)
    return comments

def read_by_editor(editor_id: str) -> list:
    """
    Return all comments made by a specific editor.
    """
    comments = []
    for comment in dbc.read(COMMENTS_COLLECT, no_id=False):
        if comment[EDITOR_ID] == editor_id:
            comments.append(comment)
    return comments

def update(comment_id: str, text: str) -> str:
    """
    Update an existing comment's text.
    """
    comment = read_one(comment_id)
    if not comment:
        raise ValueError(f"Comment with ID '{comment_id}' not found.")
    
    if not text.strip():
        raise ValueError("Comment text cannot be empty.")
    
    dbc.update(
        COMMENTS_COLLECT,
        {COMMENT_ID: to_object_id(comment_id)},
        {TEXT: text}
    )
    return comment_id

def delete(comment_id: str) -> str:
    """
    Delete a comment by its ID.
    """
    comment = read_one(comment_id)
    if not comment:
        return None
    
    del_count = dbc.delete(COMMENTS_COLLECT, {COMMENT_ID: to_object_id(comment_id)})
    return comment_id if del_count == 1 else None

def read_all() -> list:
    """
    Return all comments in the database.
    """
    return dbc.read(COMMENTS_COLLECT, no_id=False)

def main():
    pass

if __name__ == '__main__':
    main() 