import data.manuscripts.form_filler as ff

from data.manuscripts.fields import TITLE

FORM_FLDS = [
    {
        ff.FLD_NM: TITLE,
        ff.QSTN: 'Sample:',
        ff.PARAM_TYPE: ff.QUERY_STR,
    },
]
def get_fld_names() -> list:
    return ff.get_fld_names(FORM_FLDS)

def main():
    print(f'Field names: {get_fld_names()=}')


if __name__ == "__main__":
    main()