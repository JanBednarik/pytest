import py, pytest
from _pytest.recwarn import WarningsRecorder

def test_WarningRecorder(recwarn):
    showwarning = py.std.warnings.showwarning
    rec = WarningsRecorder()
    assert py.std.warnings.showwarning != showwarning
    assert not rec.list
    py.std.warnings.warn_explicit("hello", UserWarning, "xyz", 13)
    assert len(rec.list) == 1
    py.std.warnings.warn(DeprecationWarning("hello"))
    assert len(rec.list) == 2
    warn = rec.pop()
    assert str(warn.message) == "hello"
    l = rec.list
    rec.clear()
    assert len(rec.list) == 0
    assert l is rec.list
    pytest.raises(AssertionError, "rec.pop()")
    rec.finalize()
    assert showwarning == py.std.warnings.showwarning

def test_recwarn_functional(testdir):
    reprec = testdir.inline_runsource("""
        import warnings
        oldwarn = warnings.showwarning
        def test_method(recwarn):
            assert warnings.showwarning != oldwarn
            warnings.warn("hello")
            warn = recwarn.pop()
            assert isinstance(warn.message, UserWarning)
        def test_finalized():
            assert warnings.showwarning == oldwarn
    """)
    res = reprec.countoutcomes()
    assert tuple(res) == (2, 0, 0), res

#
# ============ test pytest.deprecated_call() ==============
#

def dep(i):
    if i == 0:
        py.std.warnings.warn("is deprecated", DeprecationWarning)
    return 42

reg = {}
def dep_explicit(i):
    if i == 0:
        py.std.warnings.warn_explicit("dep_explicit", category=DeprecationWarning,
                                      filename="hello", lineno=3)

def test_deprecated_call_raises():
    excinfo = pytest.raises(AssertionError,
                   "pytest.deprecated_call(dep, 3)")
    assert str(excinfo).find("did not produce") != -1

def test_deprecated_call():
    pytest.deprecated_call(dep, 0)

def test_deprecated_call_ret():
    ret = pytest.deprecated_call(dep, 0)
    assert ret == 42

def test_deprecated_call_preserves():
    onceregistry = py.std.warnings.onceregistry.copy()
    filters = py.std.warnings.filters[:]
    warn = py.std.warnings.warn
    warn_explicit = py.std.warnings.warn_explicit
    test_deprecated_call_raises()
    test_deprecated_call()
    assert onceregistry == py.std.warnings.onceregistry
    assert filters == py.std.warnings.filters
    assert warn is py.std.warnings.warn
    assert warn_explicit is py.std.warnings.warn_explicit

def test_deprecated_explicit_call_raises():
    pytest.raises(AssertionError,
                   "pytest.deprecated_call(dep_explicit, 3)")

def test_deprecated_explicit_call():
    pytest.deprecated_call(dep_explicit, 0)
    pytest.deprecated_call(dep_explicit, 0)

