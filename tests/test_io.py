import io
import os

import pytest

import omnio


def test_read_binary():
    data = os.urandom(1000)
    stream = io.BytesIO(data)

    with omnio.io.Reader(stream, encoding=None) as reader:
        assert reader.read() == data


def test_read_n_binary():
    data = b'one\ntwo\nthree'
    stream = io.BytesIO(data)

    with omnio.io.Reader(stream, encoding=None) as reader:
        assert reader.read(5) == data[:5]


def test_read_encoding():
    data = b'one\ntwo\nthree'
    stream = io.BytesIO(data)

    with omnio.io.Reader(stream, 'utf-8') as reader:
        assert reader.read() == 'one\ntwo\nthree'


def test_read_n_decoder():
    data = b'one\ntwo\nthree'
    stream = io.BytesIO(data)

    with omnio.io.Reader(stream, 'utf-8') as reader:
        assert reader.read(5) == 'one\nt'


def test_iter():
    data = b'one\ntwo\nthree four'
    stream = io.BytesIO(data)

    with omnio.io.Reader(stream, 'utf-8') as reader:
        assert next(reader) == 'one\n'
        assert next(reader) == 'two\n'
        assert next(reader) == 'three four'


def test_iter_lines():
    lines = [b'0'*512 + b'\n', b'1'*666 + b'\n', b'2'*256]
    stream = io.BytesIO(b''.join(lines))

    with omnio.io.Reader(stream, encoding=None) as reader:
        for expected, data in zip(lines, reader):
            print(len(data), len(expected))
            assert data == expected


def test_readlines():
    data = b'one\ntwo\nthree four'
    stream = io.BytesIO(data)

    with omnio.io.Reader(stream, encoding=None) as reader:
        assert reader.readlines() == [b'one\n', b'two\n', b'three four']


def test_closed():
    data = b'one\ntwo\nthree four'
    stream = io.BytesIO(data)
    f = omnio.io.Reader(stream, encoding=None)
    f.close()

    # none of these operations are allowed on a closed file
    with pytest.raises(ValueError):
        f.read()
    with pytest.raises(ValueError):
        f.readlines()
    with pytest.raises(ValueError):
        next(f)
    with pytest.raises(ValueError):
        iter(f)
