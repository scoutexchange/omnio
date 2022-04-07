import glob as python_glob

from omnio import glob


def test_escape():
    assert callable(glob.escape)
    assert glob.escape is python_glob.escape


def test_glob_path():
    assert callable(glob.glob)


def test_iglob():
    assert callable(glob.iglob)
