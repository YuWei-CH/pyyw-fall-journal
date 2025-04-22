# people.py
import re
import uuid
import data.roles as rls
import data.db_connect as dbc

MIN_USER_NAME_LEN = 2
PEOPLE_COLLECT = 'people'

# field keys
ID          = 'id'
NAME        = 'name'
ROLES       = 'roles'
AFFILIATION = 'affiliation'
EMAIL       = 'email'
BIO         = 'bio'

client = dbc.connect_db()

CHAR_OR_DIGIT = '[A-Za-z0-9]'

def is_valid_email(email: str) -> bool:
    pattern = (
        rf"^(?!.*\.\.)"                    # no consecutive '.'
        rf"{CHAR_OR_DIGIT}[A-Za-z0-9._%+-]*"
        rf"@{CHAR_OR_DIGIT}[A-Za-z0-9.-]*"
        r"\.[A-Za-z]{2,10}$"
    )
    return bool(re.match(pattern, email))


def read() -> dict:
    """Return all users keyed by UUID."""
    recs = dbc.read(PEOPLE_COLLECT)  # get a list of dicts
    out = {}
    for rec in recs:
        key = rec.get(ID) or rec.get(EMAIL)
        out[key] = rec
    return out

def read_one(identifier: str) -> dict:
    """
    Lookup by UUID or email.
    """
    rec = dbc.read_one(PEOPLE_COLLECT, {ID: identifier})
    if rec:
        return rec
    return dbc.read_one(PEOPLE_COLLECT, {EMAIL: identifier})


def exists(identifier: str) -> bool:
    return read_one(identifier) is not None

def is_valid_person(name, affiliation, email, role=None, roles=None, bio=None) -> bool:
    if not is_valid_email(email):
        raise ValueError(f'Invalid email: {email}')
    if not name.strip() or not affiliation.strip():
        raise ValueError("Name and affiliation can't be blank.")
    for r in ([role] if role else roles or []):
        if not rls.is_valid(r):
            raise ValueError(f'Invalid role: {r}')
    return True


def create(name: str, affiliation: str, email: str, role: str, bio: str = "") -> dict:
    """Create a user with a generated UUID, return full record."""
    if exists(email):
        raise ValueError(f'Duplicate email: {email}')
    if is_valid_person(name, affiliation, email, role=role):
        new_id = str(uuid.uuid4())
        person = {
            ID:          new_id,
            NAME:        name,
            AFFILIATION: affiliation,
            EMAIL:       email,
            ROLES:       [role] if role else [],
            BIO:         bio or ""
        }
        dbc.create(PEOPLE_COLLECT, person)
        return person


def update(identifier: str, name: str, affiliation: str, bio: str = None) -> dict:
    """Update name/affiliation/bio by UUID or email, return updated record."""
    rec = read_one(identifier)
    if not rec:
        raise ValueError(f'No such user: {identifier}')
    if is_valid_person(name, affiliation, rec[EMAIL]):
        fields_to_set = {NAME: name, AFFILIATION: affiliation}
        if bio is not None:
            fields_to_set[BIO] = bio
        dbc.update(PEOPLE_COLLECT, {ID: rec[ID]}, fields_to_set)
        return read_one(rec[ID])


def delete(identifier: str) -> dict:
    """Delete by UUID or email, return the deleted record."""
    rec = read_one(identifier)
    if not rec:
        return None
    count = dbc.delete(PEOPLE_COLLECT, {ID: rec[ID]})
    return rec if count == 1 else None


def add_role(identifier: str, role: str) -> dict:
    """Add a role, return full updated record."""
    rec = read_one(identifier)
    if not rec:
        raise ValueError(f'No such user: {identifier}')
    if role in rec[ROLES]:
        raise ValueError("Duplicate role.")
    rec[ROLES].append(role)
    dbc.update(PEOPLE_COLLECT, {ID: rec[ID]}, {ROLES: rec[ROLES]})
    return read_one(rec[ID])


def delete_role(identifier: str, role: str) -> dict:
    """Remove a role, return full updated record."""
    rec = read_one(identifier)
    if not rec:
        raise ValueError(f'No such user: {identifier}')
    if role not in rec[ROLES]:
        raise ValueError("Role not found.")
    rec[ROLES].remove(role)
    dbc.update(PEOPLE_COLLECT, {ID: rec[ID]}, {ROLES: rec[ROLES]})
    return read_one(rec[ID])


def get_all_people() -> list:
    people = read()
    return [f"{p[NAME]} ({p[EMAIL]})" for p in people.values()]

def get_masthead():
    """
    Return only those people who are editors (ED) or managing editors (ME).
    """
    all_people = read()
    return {
        user_id: { 'name': p['name'], 'email': p['email'], 'roles': p['roles'] }
        for user_id, p in all_people.items()
        if any(r in ('ED','ME') for r in p.get('roles', []))
    }

def main():
    print(get_masthead())


if __name__ == '__main__':
    main()
