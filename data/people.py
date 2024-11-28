import re
import data.roles as rls
import data.db_connect as dbc
from data.roles import MNG_EDITOR_CODE, EDITOR_CODE

MIN_USER_NAME_LEN = 2

PEOPLE_COLLECT = 'people'

# fields
NAME = 'name'
ROLES = 'roles'
AFFILIATION = 'affiliation'
EMAIL = 'email'

TEST_EMAIL = 'testEmail@nyu.edu'
DEL_EMAIL = 'deleteEmail@nyu.edu'

# for re check
CHAR_OR_DIGIT = '[A-Za-z0-9]'


client = dbc.connect_db()
print(f'{client=}')

# Initialization
people_dict = {
    TEST_EMAIL: {
        NAME: 'Yuxuan Wang',
        ROLES: [MNG_EDITOR_CODE],
        AFFILIATION: 'THU',
        EMAIL: TEST_EMAIL,
    },
    DEL_EMAIL: {
        NAME: 'Yuwei Sun',
        ROLES: [EDITOR_CODE],
        AFFILIATION: 'PKU',
        EMAIL: DEL_EMAIL,
    },
}
people_db = dbc.read_dict(PEOPLE_COLLECT, EMAIL)
for person in people_dict:
    if person not in people_db:
        dbc.create(PEOPLE_COLLECT, people_dict[person])
    else:
        dbc.del_one(PEOPLE_COLLECT, {EMAIL: person})
        dbc.create(PEOPLE_COLLECT, people_dict[person])


def is_valid_email(email: str) -> bool:
    pattern = (
        rf"^(?!.*\.\.)"                    # no consecutive '.'
        rf"{CHAR_OR_DIGIT}[a-zA-Z0-9._%+-]*"
        rf"@{CHAR_OR_DIGIT}[a-zA-Z0-9.-]*"
        r"\.[a-zA-Z]{2,10}$"
    )
    return bool(re.match(pattern, email))


def read():
    """
    Our contract:
        - No arguments.
        - Returns a dictionary of users keyed on user email.
        - Each user email must be the key for another dictionary.
    """
    people = dbc.read_dict(PEOPLE_COLLECT, EMAIL)
    print(f'{people=}')
    return people


def read_one(email: str) -> dict:
    """
    Return a person record if email present in DB,
    else None.
    """
    return dbc.read_one(PEOPLE_COLLECT, {EMAIL: email})


def exists(email: str) -> bool:
    return read_one(email) is not None


def is_valid_person(name: str, affiliation: str, email: str,
                    role: str = None, roles: list = None) -> bool:
    people_db = dbc.read_dict(PEOPLE_COLLECT, EMAIL)
    if email in people_db:
        raise ValueError(f'Adding duplicate {email=}')
    if not is_valid_email(email):
        raise ValueError(f'Invalid email: {email}')
    if not name.strip() or not affiliation.strip():
        raise ValueError("Name or Affiliation can't be blank. ")
    if role:
        if not rls.is_valid(role):
            raise ValueError(f'Invalid role: {role}')
    elif roles:
        for role in roles:
            if not rls.is_valid(role):
                raise ValueError(f'Invalid role: {role}')
    return True


def create(name: str, affiliation: str, email: str, role: str):
    if exists(email):
        raise ValueError(f'Adding duplicate {email=}')
    if is_valid_person(name, affiliation, email, role=role):
        roles = []
        if role:
            roles.append(role)
        person = {
            NAME: name,
            AFFILIATION: affiliation,
            EMAIL: email,
            ROLES: [role]
        }
        print(person)
        dbc.create(PEOPLE_COLLECT, person)
        return email


def delete(email):
    del_num = dbc.del_one(PEOPLE_COLLECT, {EMAIL: email})
    return email if del_num == 1 else None


def update(email: str, field: str, value: str):
    if not value.strip():
        raise ValueError("Value can't be blank")
    if field != NAME and field != AFFILIATION:
        raise ValueError(f'{field} is not a valid field to update')
    result = dbc.update_doc(PEOPLE_COLLECT, {EMAIL: email}, {field: value})
    if result.matched_count > 0:
        return email
    return None


def has_role(person: dict, role):
    if role in person.get(ROLES):
        return True
    return False


MH_FIELDS = [NAME, AFFILIATION]


def create_mh_rec(person: dict) -> dict:
    mh_rec = {}
    for field in MH_FIELDS:
        mh_rec[field] = person.get(field, '')
    return mh_rec


def get_masthead() -> dict:
    masthead = {}
    mh_roles = rls.get_masthead_roles()
    for mh_role, text in mh_roles.items():
        people_w_role = []
        people = read()
        for _id, person in people.items():
            if has_role(person, mh_role):
                rec = create_mh_rec(person)
                people_w_role.append(rec)
            masthead[text] = people_w_role
    return masthead


def add_role(email: str, role: str):
    if not role.strip():
        raise ValueError("Can't add an empty role")
    person = dbc.read_one(PEOPLE_COLLECT, {EMAIL: email})
    if not person:
        raise ValueError(f"Person {email} not found")
    if role in person.get(ROLES, []):
        raise ValueError("Can't add a duplicate role")
    updated_roles = person[ROLES] + [role]
    dbc.update_doc(PEOPLE_COLLECT, {EMAIL: email}, {ROLES: updated_roles})
    return email


def delete_role(email: str, role: str):
    if not role.strip():
        raise ValueError("Can't delete an empty role")
    person = dbc.read_one(PEOPLE_COLLECT, {EMAIL: email})
    if not person:
        raise ValueError(f"Person {email} not found")
    if role not in person.get(ROLES, []):
        raise ValueError("Role not found")
    updated_roles = [r for r in person[ROLES] if r != role]
    dbc.update_doc(PEOPLE_COLLECT, {EMAIL: email}, {ROLES: updated_roles})
    return email
