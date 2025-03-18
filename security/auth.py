import data.people as ppl
import data.db_connect as dbc
import data.roles as rls

PASSWORD = 'pw'


def register_user(username: str, password: str,
                  name: str, affiliation: str = "Unknown",
                  bio: str = "") -> bool:
    """
    If 'username' doesn't exist in 'people', create them with:
      - email = username
      - pw = password (plain text for demonstration)
      - roles = ['AU']  (default role)
      - name = name
      - affiliation = affiliation
      - bio = bio
    Return True if created, False if user already existed.
    """
    existing_user = ppl.read_one(username)
    if existing_user:
        return False
    ppl.create(
        name=name,
        affiliation=affiliation,
        email=username,
        role=rls.AUTHOR_CODE,       # default role
        bio=bio,
    )
    dbc.update(
        collection=ppl.PEOPLE_COLLECT,
        filters={ppl.EMAIL: username},
        update_dict={PASSWORD: password}
    )
    return True


def authenticate_user(username, password):
    user_record = ppl.read_one(username)
    if not user_record:
        return None
    if user_record.get(PASSWORD) == password:
        return {
            ppl.EMAIL: user_record[ppl.EMAIL],
            ppl.NAME: user_record.get(ppl.NAME, user_record[ppl.EMAIL]),
            ppl.ROLES: user_record.get(ppl.ROLES, []),
        }
    return None
