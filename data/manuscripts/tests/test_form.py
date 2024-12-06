import data.manuscripts.form as mform
from data.manuscripts.fields import TITLE, TEST_FLD_DISP_NM


def test_get_fld_names():
    names = mform.get_fld_names()
    assert isinstance(names, list)
