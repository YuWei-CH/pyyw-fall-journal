import security.db_connect as dbc

USER_COLLECTION = 'users'  # Collection for storing user credentials


def register_user(username: str, password: str) -> bool:
    """
    Registers a new user by storing their username and password.
    """
    if dbc.read_one(USER_COLLECTION, {'_id': username}):
        print("User already exists.")
        return False  # Username is already taken
    dbc.create(USER_COLLECTION, {'_id': username, 'password': password})
    print("User registered successfully.")
    return True


def authenticate_user(username: str, password: str) -> bool:
    """
    Authenticates a user by checking their stored password.
    """
    user = dbc.read_one(USER_COLLECTION, {'_id': username})
    if not user:
        print("User not found.")
        return False
    if password == user['password']:
        print("Login successful.")
        return True
    print("Invalid password.")
    return False
