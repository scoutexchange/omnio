import io
import os

import pytest

import omnio


def test_read_binary():
    data = os.urandom(1000)
    stream = io.BytesIO(data)

    with omnio.io.Reader(stream) as reader:
        assert reader.read() == data


def test_read_n_binary():
    data = b'one\ntwo\nthree'
    stream = io.BytesIO(data)

    with omnio.io.Reader(stream) as reader:
        assert reader.read(5) == data[:5]


def test_iter():
    data = b'one\ntwo\nthree four'
    stream = io.BytesIO(data)

    with omnio.io.Reader(stream) as reader:
        assert next(reader) == b'one\n'
        assert next(reader) == b'two\n'
        assert next(reader) == b'three four'


def test_iter_lines():
    lines = [b'0'*512 + b'\n', b'1'*666 + b'\n', b'2'*256]
    stream = io.BytesIO(b''.join(lines))

    with omnio.io.Reader(stream) as reader:
        for expected, data in zip(lines, reader):
            print(len(data), len(expected))
            assert data == expected


def test_closed():
    data = b'one\ntwo\nthree four'
    stream = io.BytesIO(data)
    f = omnio.io.Reader(stream)
    f.close()

    # none of these operations are allowed on a closed file
    with pytest.raises(ValueError):
        f.read()
    with pytest.raises(ValueError):
        next(f)
    with pytest.raises(ValueError):
        iter(f)
