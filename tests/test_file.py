import bz2
import csv
import gzip
import os

import omnio


def test_open_file_r():
    with omnio.open('tests/data/test_open_file_r.txt', 'r') as fd:
        assert fd.read() == b'one\ntwo\nthree\n'


def test_open_file_rtz():
    with omnio.open('tests/data/flights-3m.csv.gz', 'rtz') as fd:
        reader = csv.reader(fd)
        headers = next(reader)
        assert headers == \
            ['date', 'delay', 'distance', 'origin', 'destination']
        data = list(reader)
        assert len(data) == 231083  # number data rows


def test_open_file_rbz():
    with omnio.open('tests/data/flights-3m.csv.gz', 'rbz') as fd:
        data = fd.read()
        assert type(data) is bytes
        assert len(data) == 5535530  # uncompressed file size


def test_open_file_rbj():
    with omnio.open('tests/data/flights-3m.csv.bz2', 'rbj') as fd:
        data = fd.read()
        assert type(data) is bytes
        assert len(data) == 5535530  # uncompressed file size


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


def test_open_file_wbz():
    path = 'tests/data/test_open_file_wbz.txt.gz'
    data = os.urandom(1024)
    try:
        with omnio.open(path, 'wbz') as fd:
            fd.write(data)
    except:
        raise
    else:
        with open(path, 'rb') as fd:
            with gzip.open(fd) as gz:
                assert gz.read() == data
    finally:
        os.remove(path)


def test_open_file_wbj():
    path = 'tests/data/test_open_file_wbj.txt.gz'
    data = os.urandom(1024)
    try:
        with omnio.open(path, 'wbj') as fd:
            fd.write(data)
    except:
        raise
    else:
        with open(path, 'rb') as fd:
            with bz2.open(fd) as gz:
                assert gz.read() == data
    finally:
        os.remove(path)


def test_open_file_wtz():
    path = 'tests/data/test_open_file_wtz.txt.gz'
    data = 'unicode string to be seamlessly compressed'
    try:
        with omnio.open(path, 'wtz') as fd:
            fd.write(data)
    except:
        raise
    else:
        with open(path, 'rb') as fd:
            with gzip.open(fd, 'rt') as gz:
                assert gz.read() == data
    finally:
        os.remove(path)
