import re
import data.roles as rls

MIN_USER_NAME_LEN = 2

# fields
NAME = 'name'
ROLES = 'roles'
AFFILIATION = 'affiliation'
EMAIL = 'email'

TEST_EMAIL = 'testEmail@nyu.edu'
DEL_EMAIL = 'deleteEmail@nyu.edu'


people_dict = {
    TEST_EMAIL: {
        NAME: 'Yuxuan Wang',
        ROLES: [],
        AFFILIATION: 'THU',
        EMAIL: TEST_EMAIL,
    },
    DEL_EMAIL: {
        NAME: 'Yuwei Sun',
        ROLES: [],
        AFFILIATION: 'PKU',
        EMAIL: DEL_EMAIL,
    },
}

# for re check
CHAR_OR_DIGIT = '[A-Za-z0-9]'


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
    people = people_dict
    return people


def is_valid_person(name: str, affiliation: str, email: str,
                    role: str) -> bool:
    if email in people_dict:
        raise ValueError(f'Adding duplicate {email=}')
    if not is_valid_email(email):
        raise ValueError(f'Invalid email: {email}')
    if not rls.is_valid(role):
        raise ValueError(f'Invalid role: {role}')
    return True


def create(name: str, affiliation: str, email: str):
    if email in people_dict:
        raise ValueError(f'Adding duplicate {email=}')
    people_dict[email] = {NAME: name, AFFILIATION: affiliation,
                          EMAIL: email}
    return email


def delete(_id):
    people = read()
    if _id in people:
        del people[_id]
        return _id
    else:
        return None


def update_name(_id: str, name: str):
    if not name.strip():
        raise ValueError("Name can't be blank")
    if _id in people_dict:
        people_dict[_id][NAME] = name
        return _id
    else:
        return None


def update_affiliation(_id: str, affiliation: str):
    """
    Updates the affiliation of an existing user.
    """
    if not affiliation.strip():
        raise ValueError("Affiliation can't be blank")
    if _id in people_dict:
        people_dict[_id][AFFILIATION] = affiliation
        return _id
    else:
        return None


def has_role(person, role):
    if role in person[ROLES]:
        return True
    return False


def get_masthead() -> dict:
    masthead = {}
    mh_roles = rls.get_masthead_roles()
    for mh_role, text in mh_roles.items():
        people_w_role = []
        people = read()
        for _id, person in people.items():
            # if has_role(person, mh_role):
            #   rec = create_mh_rec(person)
            #   people_w_role.append(rec)
            masthead[text] = people_w_role
    return masthead
