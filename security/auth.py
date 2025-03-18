import data.people as ppl
import data.db_connect as dbc


def register_user(username: str, password: str) -> bool:
    """
    If 'username' doesn't exist in 'people', create them with:
      - email=username
      - pw=password (plain text for demonstration)
      - roles=['AU']  (default role)
      - name=username, affiliation='Unknown'
    Return True if created, False if user already existed.
    """
    existing_user = ppl.read_one(username)
    if existing_user:
        return False
    ppl.create(
        name=username,
        affiliation="Unknown",
        email=username,
        role="AU",       # default role
        bio="",          # no bio
    )
    dbc.update(
        collection='people',
        filters={'email': username},
        update_dict={'pw': password}
    )
    return True


def authenticate_user(username, password):
    user_record = ppl.read_one(username)
    if not user_record:
        return None
    if user_record.get('pw') == password:
        return {
            'email': user_record['email'],
            'name': user_record.get('name', user_record['email']),
            'roles': user_record.get('roles', []),
        }
    return None
