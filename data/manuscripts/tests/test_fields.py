import data.manuscripts.fields as mflds
from data.manuscripts.fields import TEST_FLD_NM, TEST_FLD_DISP_NM


def test_get_flds():
    assert isinstance(mflds.get_flds(), dict)


def test_get_fld_names():
    assert isinstance(mflds.get_fld_names(), list)


def test_get_disp_name():
    disp_name = mflds.get_disp_name(TEST_FLD_NM)
    assert isinstance(disp_name, str)
    assert disp_name == TEST_FLD_DISP_NM
