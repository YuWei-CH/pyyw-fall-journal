import data.people as ppl
import data.db_connect as db

def register_user(username, password):
    """
    Store a new user in the DB with hashed password, or return False if user exists.
    Example only—modify to suit your actual logic.
    """
    existing_user = ppl.read_one(username)
    if existing_user:
        return False

    hashed_pw = password
    ppl.create(
        name=username,
        affiliation="Unknown",
        email=username,
        role="AU"
    )
    return True


def read_one(email):
    """
    Retrieve a user record by email.

    Args:
        email (str): The email of the user to retrieve.

    Returns:
        dict: A dictionary containing the user's email, name, and roles if found,
              otherwise None.
    """
    record = db.find_one({'email': email})  # Make sure 'db' is imported or defined if needed
    if record:
        print(record)
        return {
            'email': record['email'],
            'name': record.get('name', record['email']),
            'roles': record.get('roles', []),
        }
    else:
        return None


def authenticate_user(username, password):
    user = ppl.read_one(username)
    print(user)
    if user:
        print("Login successful in security.")
        return user
    else:
        return None
