import pytest
import data.comment as cmt
import data.manuscript as msc
import data.people as ppl
from data.roles import ED_CODE

# Test data
TEST_MANUSCRIPT_TITLE = "Test Manuscript for Comments"
TEST_MANUSCRIPT_AUTHOR = "Test Author"
TEST_MANUSCRIPT_AUTHOR_EMAIL = "testAuthorForComments@gmail.com"
TEST_MANUSCRIPT_TEXT = "Test Manuscript Text"
TEST_MANUSCRIPT_ABSTRACT = "Test Manuscript Abstract"
TEST_MANUSCRIPT_EDITOR_EMAIL = "testEditorForComments@gmail.com"

TEST_EDITOR_NAME = "Test Editor"
TEST_EDITOR_AFFILIATION = "Test University"
TEST_EDITOR_EMAIL = "testEditorForComments@gmail.com"

TEST_COMMENT_TEXT = "This is a test comment on the manuscript."

@pytest.fixture(scope='function')
def temp_manuscript():
    """Create a temporary manuscript for testing comments."""
    manu_id = msc.create(
        TEST_MANUSCRIPT_TITLE,
        TEST_MANUSCRIPT_AUTHOR,
        TEST_MANUSCRIPT_AUTHOR_EMAIL,
        TEST_MANUSCRIPT_TEXT,
        TEST_MANUSCRIPT_ABSTRACT,
        TEST_MANUSCRIPT_EDITOR_EMAIL
    )
    yield manu_id
    # Clean up after test
    try:
        msc.delete(manu_id)
    except:
        print('Manuscript already deleted.')

@pytest.fixture(scope='function')
def temp_editor():
    """Create a temporary editor for testing comments."""
    editor_id = ppl.create(
        TEST_EDITOR_NAME,
        TEST_EDITOR_AFFILIATION,
        TEST_EDITOR_EMAIL,
        ED_CODE
    )
    yield editor_id
    # Clean up after test
    try:
        ppl.delete(editor_id)
    except:
        print('Editor already deleted.')

@pytest.fixture(scope='function')
def temp_comment(temp_manuscript, temp_editor):
    """Create a temporary comment for testing."""
    comment_id = cmt.create(
        temp_manuscript,
        temp_editor,
        TEST_COMMENT_TEXT
    )
    yield comment_id
    # Clean up after test
    try:
        cmt.delete(comment_id)
    except:
        print('Comment already deleted.')

def test_create(temp_manuscript, temp_editor):
    """Test creating a new comment."""
    comment_id = cmt.create(
        temp_manuscript,
        temp_editor,
        TEST_COMMENT_TEXT
    )
    assert comment_id is not None
    
    # Clean up
    cmt.delete(comment_id)

def test_create_empty_text(temp_manuscript, temp_editor):
    """Test creating a comment with empty text."""
    with pytest.raises(ValueError):
        cmt.create(temp_manuscript, temp_editor, "")

def test_create_invalid_manuscript(temp_editor):
    """Test creating a comment with an invalid manuscript ID."""
    with pytest.raises(ValueError):
        cmt.create("invalid_manuscript_id", temp_editor, TEST_COMMENT_TEXT)

def test_create_invalid_editor(temp_manuscript):
    """Test creating a comment with an invalid editor ID."""
    with pytest.raises(ValueError):
        cmt.create(temp_manuscript, "invalid_editor_id", TEST_COMMENT_TEXT)

def test_read_one(temp_comment, temp_manuscript):
    """Test reading a single comment by ID."""
    comment = cmt.read_one(temp_comment)
    assert comment is not None
    assert comment[cmt.MANUSCRIPT_ID] == temp_manuscript
    assert comment[cmt.TEXT] == TEST_COMMENT_TEXT

def test_read_one_not_found():
    """Test reading a non-existent comment."""
    comment = cmt.read_one("non_existent_id")
    assert comment is None

def test_read_by_manuscript(temp_comment, temp_manuscript):
    """Test reading comments by manuscript ID."""
    comments = cmt.read_by_manuscript(temp_manuscript)
    assert len(comments) > 0
    assert any(c[cmt.COMMENT_ID] == temp_comment for c in comments)

def test_read_by_editor(temp_comment, temp_editor):
    """Test reading comments by editor ID."""
    comments = cmt.read_by_editor(temp_editor)
    assert len(comments) > 0
    assert any(c[cmt.COMMENT_ID] == temp_comment for c in comments)

def test_update(temp_comment):
    """Test updating a comment's text."""
    new_text = "Updated comment text"
    updated_id = cmt.update(temp_comment, new_text)
    assert updated_id == temp_comment
    
    # Verify the update
    comment = cmt.read_one(temp_comment)
    assert comment[cmt.TEXT] == new_text

def test_update_empty_text(temp_comment):
    """Test updating a comment with empty text."""
    with pytest.raises(ValueError):
        cmt.update(temp_comment, "")

def test_update_not_found():
    """Test updating a non-existent comment."""
    with pytest.raises(ValueError):
        cmt.update("non_existent_id", "New text")

def test_delete(temp_comment):
    """Test deleting a comment."""
    deleted_id = cmt.delete(temp_comment)
    assert deleted_id == temp_comment
    
    # Verify deletion
    comment = cmt.read_one(temp_comment)
    assert comment is None

def test_delete_not_found():
    """Test deleting a non-existent comment."""
    deleted_id = cmt.delete("non_existent_id")
    assert deleted_id is None

def test_read_all(temp_comment):
    """Test reading all comments."""
    comments = cmt.read_all()
    assert len(comments) > 0
    assert any(c[cmt.COMMENT_ID] == temp_comment for c in comments)

def test_is_valid_comment(temp_manuscript, temp_editor):
    """Test the validation function for comments."""
    assert cmt.is_valid_comment(temp_manuscript, temp_editor, TEST_COMMENT_TEXT)

def test_is_valid_comment_empty_text(temp_manuscript, temp_editor):
    """Test validation with empty text."""
    with pytest.raises(ValueError):
        cmt.is_valid_comment(temp_manuscript, temp_editor, "")

def test_is_valid_comment_invalid_manuscript(temp_editor):
    """Test validation with invalid manuscript ID."""
    with pytest.raises(ValueError):
        cmt.is_valid_comment("invalid_manuscript_id", temp_editor, TEST_COMMENT_TEXT)

def test_is_valid_comment_invalid_editor(temp_manuscript):
    """Test validation with invalid editor ID."""
    with pytest.raises(ValueError):
        cmt.is_valid_comment(temp_manuscript, "invalid_editor_id", TEST_COMMENT_TEXT) 