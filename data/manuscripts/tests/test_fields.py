import data.manuscripts.fields as mflds

def test_get_flds():
    flds = mflds.get_flds()
    assert isinstance(flds, dict), "get_flds() should return a dict."
    assert 'title' in flds, "'title' should be a key in the fields dict."
    assert 'disp_name' in flds['title'], "'disp_name' should be a key in the 'title' field."


def test_get_fld_names():
    names = mflds.get_fld_names()
    assert hasattr(names, '__iter__'), "get_fld_names() should return an iterable."
    names_list = list(names)
    assert 'title' in names_list, "'title' should be listed among field names."