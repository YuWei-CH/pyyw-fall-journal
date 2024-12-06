import data.manuscripts.form as fm
import data.manuscripts.form_filler as ff

def test_get_form():
    form = fm.get_form()
    assert isinstance(form, list)
    assert len(form) > 0
    for fld in form:
        # Every field must have a name!
        assert ff.FLD_NM in fld
        # And it can't be blank.
        assert len(fld[ff.FLD_NM]) > 0


def test_get_form_descr():
    form_descr = fm.get_form_descr()
    assert isinstance(form_descr, dict)


def test_get_fld_names():
    names = fm.get_fld_names()
    assert isinstance(names, list)
