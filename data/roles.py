
"""
This module manages person roles for a journal.
"""
from copy import deepcopy

AUTHOR_CODE = 'AU'
EDITOR_CODE = 'ED'
REFREE_CODE = 'RE'
MNG_EDITOR_CODE = 'ME'
CP_EDITOR_CODE = 'CE'

TEST_CODE = AUTHOR_CODE

ROLES = {
    AUTHOR_CODE: 'Author',
    EDITOR_CODE: 'Editor',
    REFREE_CODE: 'Referee',
    MNG_EDITOR_CODE: 'Managing Editor',
    CP_EDITOR_CODE: 'Copy Editor'

}

MH_ROLES = [EDITOR_CODE, MNG_EDITOR_CODE, CP_EDITOR_CODE]


def get_roles() -> dict:
    return deepcopy(ROLES)


def is_valid(code: str) -> bool:
    return code in ROLES


def get_masthead_roles() -> dict:
    mh_roles = get_roles()
    del_mh_roles = []
    for role in mh_roles:
        if role not in MH_ROLES:
            del_mh_roles.append(role)
    for del_role in del_mh_roles:
        del mh_roles[del_role]
    return mh_roles


def get_role_codes() -> list:
    return list(ROLES.keys())


def main():
    print(get_roles())
    print(get_masthead_roles())


if __name__ == '__main__':
    main()
