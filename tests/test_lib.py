import pytest

import omnio


def test_invalid_mode():
    with pytest.raises(ValueError):
        omnio.open('', 'q')


def test_invalid_combination():
    # can't combine read and write
    with pytest.raises(ValueError):
        omnio.open('', 'rw')

    # can't specify encoding in binary mode
    with pytest.raises(ValueError):
        omnio.open('', 'rb', encoding='utf-8')

    # can't specify errors in binary mode
    with pytest.raises(ValueError):
        omnio.open('', 'rb', errors='strict')

    # can't specify newline in binary mode
    with pytest.raises(ValueError):
        omnio.open('', 'rb', newline='\t')

    # can't have both text and binary
    with pytest.raises(ValueError):
        omnio.open('', 'rbt')

    # only one compression type allowed
    with pytest.raises(ValueError):
        omnio.open('', 'rjz')


def test_default_config():
    config = omnio.default_config()

    for scheme in ["file", "http", "s3"]:
        assert isinstance(config[scheme], dict)

    omnio.open("tests/data/ascii.txt", 'rt', config=config)
