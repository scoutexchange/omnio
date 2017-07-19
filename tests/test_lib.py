import os

import pytest

import omnio


def test_open_file_r():
    with omnio.open('tests/data/test_open_file_r.txt', 'r') as fd:
        assert fd.read() == 'one\ntwo\nthree\n'


def test_open_file_w():
    path = 'tests/data/test_open_file_w.txt'
    try:
        with omnio.open(path, 'wt') as fd:
            fd.write('one\ntwo\nthree\n')
    except:
        raise
    else:
        with open(path, 'r') as fd:
            assert list(fd) == ['one\n', 'two\n', 'three\n']
    finally:
        os.remove(path)


def test_invalid_mode():
    with pytest.raises(ValueError):
        omnio.open('tests/data/test_open_file_r.txt', 'q')


def test_invalid_combination():
    # can't combine read and write
    with pytest.raises(ValueError):
        omnio.open('tests/data/test_open_file_r.txt', 'rw')

    # can't specify encoding in binary mode
    with pytest.raises(ValueError):
        omnio.open('tests/data/test_open_file_r.txt', 'rb', encoding='utf-8')

    # can't have both text and binary
    with pytest.raises(ValueError):
        omnio.open('tests/data/test_open_file_r.txt', 'rbt')
