TITLE = 'title'
AUTHOR = 'author'
REFEREES = 'referees'

DISP_NAME = 'disp_name'
AUTHOR = 'author'
REFEREES = 'referees'

TEST_FLD_NM = TITLE
TEST_FLD_DISP_NM = 'Title'


FIELDS = {
    TITLE: {
        DISP_NAME: 'Title',
    },
    AUTHOR: {
        DISP_NAME: 'Author',
    },
    REFEREES: {
        DISP_NAME: 'Referees',
    },
}


def get_flds() -> dict:
    return FIELDS


def get_fld_names() -> list:
    return list(FIELDS.keys())


def get_disp_name(fld_nm: str) -> str:
    fld = FIELDS.get(fld_nm, '')
    return fld[DISP_NAME]


def main():
    print(f'{get_flds()=}')


if __name__ == '__main__':
    main()