import re
import uuid
import data.roles as rls
import data.db_connect as dbc

MIN_USER_NAME_LEN = 2
PEOPLE_COLLECT = 'people'

# field keys
ID = 'id'
NAME = 'name'
ROLES = 'roles'
AFFILIATION = 'affiliation'
EMAIL = 'email'
BIO = 'bio'

MH_FIELDS = [NAME, AFFILIATION, BIO]
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
    """
    Return all users keyed by UUID.
    """
    recs = dbc.read(PEOPLE_COLLECT)
    out = {}
    for rec in recs:
        key = rec.get(ID) or rec.get(EMAIL)
        out[key] = rec
    return out


def read_one(identifier: str) -> dict:
    """
    Lookup a user by UUID or email.
    Returns full record or None.
    """
    rec = dbc.read_one(PEOPLE_COLLECT, {ID: identifier})
    if rec:
        return rec
    return dbc.read_one(PEOPLE_COLLECT, {EMAIL: identifier})


def exists(identifier: str) -> bool:
    return read_one(identifier) is not None


def is_valid_person(name: str, affiliation: str, email: str,
                    role: str = None, roles: list = None,
                    bio: str = None) -> bool:
    if not is_valid_email(email):
        raise ValueError(f'Invalid email: {email}')
    if not name.strip() or not affiliation.strip():
        raise ValueError("Name and affiliation can't be blank.")
    for r in ([role] if role else roles or []):
        if not rls.is_valid(r):
            raise ValueError(f'Invalid role: {r}')
    return True


def create(name: str, affiliation: str,
           email: str, role: str, bio: str = "") -> str:
    """
    Create a user with a generated UUID,
    return its ID. If email exists, return existing ID.
    """
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
        return new_id


def update(identifier: str, name: str,
           affiliation: str, bio: str = None) -> str:
    """
    Update a user’s name, affiliation,
    and optional bio. Return its ID.
    """
    rec = read_one(identifier)
    if not rec:
        raise ValueError(f'No such user: {identifier}')
    if is_valid_person(name, affiliation, rec[EMAIL]):
        fields_to_set = {NAME: name, AFFILIATION: affiliation}
        if bio is not None:
            fields_to_set[BIO] = bio
        dbc.update(PEOPLE_COLLECT, {ID: rec[ID]}, fields_to_set)
        return rec[ID]


def delete(identifier: str) -> str:
    """
    Delete by UUID or email, return its ID.
    """
    rec = read_one(identifier)
    if not rec:
        return None
    count = dbc.delete(PEOPLE_COLLECT, {ID: rec[ID]})
    return rec[ID] if count == 1 else None


def add_role(identifier: str, role: str) -> str:
    """
    Add a role to the user, return its ID.
    """
    rec = read_one(identifier)
    if not rec:
        raise ValueError(f'No such user: {identifier}')
    if not rls.is_valid(role):
        raise ValueError(f'Invalid role: {role}')
    if role in rec[ROLES]:
        raise ValueError("Duplicate role.")
    updated = rec[ROLES] + [role]
    dbc.update(PEOPLE_COLLECT, {ID: rec[ID]}, {ROLES: updated})
    return rec[ID]


def delete_role(identifier: str, role: str) -> str:
    """
    Remove a role from the user, return its ID.
    """
    rec = read_one(identifier)
    if not rec:
        raise ValueError(f'No such user: {identifier}')
    if role not in rec[ROLES]:
        raise ValueError("Role not found.")
    updated = [r for r in rec[ROLES] if r != role]
    dbc.update(PEOPLE_COLLECT, {ID: rec[ID]}, {ROLES: updated})
    return rec[ID]


def get_all_people() -> list:
    """
    Return a list of "Name (email)" strings for all users.
    """
    people = read()
    return [f"{p[NAME]} ({p[EMAIL]})" for p in people.values()]


def get_mh_fields(journal_code=None) -> list:
    """
    Fields to include in a masthead record.
    """
    return MH_FIELDS


def create_mh_rec(person: dict) -> dict:
    """
    From a full person record, extract only masthead fields.
    """
    return {field: person.get(field, '') for field in MH_FIELDS}


def has_role(person: dict, role: str) -> bool:
    """
    Check if the user has the specified role.
    """
    return role in person.get(ROLES, [])


def get_masthead() -> dict:
    """
    Return only those people who are editors (ED) or managing editors (ME).
    """
    all_people = read()
    return {
        user_id: {'name': p[NAME], 'email': p[EMAIL], 'roles': p[ROLES]}
        for user_id, p in all_people.items()
        if any(r in ('ED', 'ME') for r in p.get(ROLES, []))
    }


def main():
    print(get_masthead())


if __name__ == '__main__':
    main()
