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


def read():
    """
    Our contract:
        - No arguments.
        - Returns a dictionary of users keyed on user email.
        - Each user email must be the key for another dictionary.
    """
    people = people_dict
    return people


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
