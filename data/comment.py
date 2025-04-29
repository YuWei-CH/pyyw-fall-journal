import data.db_connect as dbc
import data.manuscript as msc
import data.people as ppl
from data.roles import ED_CODE
from bson import ObjectId

COMMENTS_COLLECTION = "comments"
client = dbc.connect_db()

COMMENT_ID = "_id"
MANUSCRIPT_ID = "manuscript_id"
EDITOR_ID = "editor_id"
TEXT = "text"
TIMESTAMP = 'timestamp'


def to_object_id(id_str):
    """
    Convert a string to a Mongo ObjectId if valid, otherwise return None.
    """
    try:
        return ObjectId(id_str)
    except Exception:
        return None


def is_valid_comment(manuscript_id, editor_id, text):
    """Validate comment data."""
    if not text:
        raise ValueError("Comment text cannot be empty")

    manuscript = msc.read_one(manuscript_id)
    if not manuscript:
        raise ValueError(f"Manuscript {manuscript_id} not found")

    editor = ppl.read_one(editor_id)
    if not editor:
        raise ValueError(f"Editor {editor_id} not found")

    if not ppl.has_role(editor, ED_CODE):
        raise ValueError(f"Person {editor_id} is not an editor")

    return True


def create(manuscript_id, editor_id, text):
    """Create a new comment."""
    if not is_valid_comment(manuscript_id, editor_id, text):
        raise ValueError("Invalid comment data")

    comment = {
        MANUSCRIPT_ID: manuscript_id,
        EDITOR_ID: editor_id,
        TEXT: text
    }

    result = dbc.create(COMMENTS_COLLECTION, comment)
    return str(result.inserted_id)


def read_one(comment_id):
    """Read a single comment by ID."""
    obj_id = to_object_id(comment_id)
    if not obj_id:
        return None
    return dbc.read_one(COMMENTS_COLLECTION, {COMMENT_ID: obj_id})


def read_by_manuscript(manuscript_id):
    """Read all comments for a manuscript."""
    comments = dbc.read(COMMENTS_COLLECTION, no_id=False)
    return [c for c in comments if c[MANUSCRIPT_ID] == manuscript_id]


def read_by_editor(editor_id):
    """Read all comments by an editor."""
    comments = dbc.read(COMMENTS_COLLECTION, no_id=False)
    return [c for c in comments if c[EDITOR_ID] == editor_id]


def update(comment_id, text):
    """Update a comment's text."""
    if not text:
        raise ValueError("Comment text cannot be empty")

    comment = read_one(comment_id)
    if not comment:
        raise ValueError(f"Comment {comment_id} not found")

    obj_id = to_object_id(comment_id)
    if not obj_id:
        raise ValueError(f"Invalid comment ID: {comment_id}")
    dbc.update(
        COMMENTS_COLLECTION,
        {COMMENT_ID: obj_id},
        {TEXT: text}
    )
    return comment_id


def delete(comment_id):
    """Delete a comment."""
    comment = read_one(comment_id)
    if not comment:
        return None
    obj_id = to_object_id(comment_id)
    if not obj_id:
        return None

    result = dbc.delete(COMMENTS_COLLECTION, {COMMENT_ID: obj_id})
    return comment_id if result > 0 else None


def read_all():
    """Read all comments."""
    return dbc.read(COMMENTS_COLLECTION, no_id=False)


def main():
    pass


if __name__ == '__main__':
    main()
