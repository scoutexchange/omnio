import pytest

import omnio


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

    # only one compression type allowed
    with pytest.raises(ValueError):
        omnio.open('tests/data/test_open_file_r.txt', 'rjz')
