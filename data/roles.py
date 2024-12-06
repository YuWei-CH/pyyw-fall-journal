
"""
This module manages person roles for a journal.
"""
from copy import deepcopy

ED_CODE = 'ED'
ME_CODE = 'ME'
CE_CODE = 'CE'
AUTHOR_CODE = 'AU'
REFREE_CODE = 'RE'

TEST_CODE = AUTHOR_CODE

ROLES = {
    ED_CODE: 'Editor',
    ME_CODE: 'Managing Editor',
    CE_CODE: 'Consulting Editor',
    AUTHOR_CODE: 'Author',
    REFREE_CODE: 'Referee',
}

MH_ROLES = [ED_CODE, ME_CODE, CE_CODE]


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
