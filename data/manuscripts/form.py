import data.manuscripts.form_filler as ff

from data.manuscripts.fields import TITLE

FORM_FLDS = [
    {
        ff.FLD_NM: TITLE,
        ff.QSTN: 'Sample:',
        ff.PARAM_TYPE: ff.QUERY_STR,
    },
]


def get_form() -> list:
    return FORM_FLDS


def get_form_descr():
    """
    For Swagger!
    """
    return ff.get_form_descr(FORM_FLDS)


def get_fld_names() -> list:
    return ff.get_fld_names(FORM_FLDS)


def main():
    print(f'Form: {get_form()=}')
    print(f'Form: {get_form_descr()=}')
    print(f'Field names: {get_fld_names()=}')


if __name__ == "__main__":
    main()