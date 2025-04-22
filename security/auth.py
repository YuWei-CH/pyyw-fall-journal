import data.people as ppl
import data.db_connect as dbc
import data.roles as rls

PASSWORD = 'pw'


def register_user(username: str,
                  password: str,
                  name: str,
                  affiliation: str = "Unknown",
                  role: str = rls.AUTHOR_CODE,
                  bio: str = "") -> bool:
    """
    Create a new user. Returns True on success, False if user already exists.
    """
    if ppl.read_one(username):
        return False

    ppl.create(
        name=name,
        affiliation=affiliation,
        email=username,
        role=role,
        bio=bio,
    )
    dbc.update(
        collection=ppl.PEOPLE_COLLECT,
        filters={ppl.EMAIL: username},
        update_dict={PASSWORD: password}
    )

    return True


def authenticate_user(username: str, password: str) -> dict:
    """
    Returns a dict {id, email, name, roles} on valid credentials, or None.
    """
    rec = ppl.read_one(username)
    if not rec or rec.get(PASSWORD) != password:
        return None

    return {
        ppl.ID:    rec[ppl.ID],
        ppl.EMAIL: rec[ppl.EMAIL],
        ppl.NAME:  rec.get(ppl.NAME, rec[ppl.EMAIL]),
        ppl.ROLES: rec.get(ppl.ROLES, []),
    }
