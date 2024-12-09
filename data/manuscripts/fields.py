TITLE = 'title'
TITLE_DISP_NM = 'Title'
AUTHOR = 'author'
AUTHOR_DISP_NM = 'Author'
REFEREES = 'referees'
REFEREES_DISP_NM = 'Referees'

DISP_NAME = 'disp_name'
TEST_FLD_NM = TITLE
TEST_FLD_DISP_NM = TITLE_DISP_NM


FIELDS = {
    TITLE: {
        DISP_NAME: TITLE_DISP_NM,
    },
    AUTHOR: {
        DISP_NAME: AUTHOR_DISP_NM,
    },
    REFEREES: {
        DISP_NAME: REFEREES_DISP_NM,
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