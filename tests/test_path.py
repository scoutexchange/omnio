import bz2
import csv
import gzip
import os

import omnio


def test_rt_ascii():
    path = 'tests/data/ascii.txt'
    with omnio.open(path, 'rt', encoding='ascii') as fd:
        data = fd.read()
        assert type(data) is str
        assert len(data) == 1392


def test_rt_iso8859():
    path = 'tests/data/iso-8859-1.txt'
    with omnio.open(path, 'rt', encoding='iso-8859-1') as fd:
        data = fd.read()
        assert type(data) is str
        assert len(data) == 700


def test_rt_utf8():
    path = 'tests/data/utf-8.txt'
    with omnio.open(path, 'rt', encoding='utf-8') as fd:
        data = fd.read()
        assert type(data) is str
        assert len(data) == 874


def test_rtz():
    with omnio.open('tests/data/flights-3m.csv.gz', 'rtz') as fd:
        reader = csv.reader(fd)
        headers = next(reader)
        assert headers == \
            ['date', 'delay', 'distance', 'origin', 'destination']
        data = list(reader)
        assert len(data) == 231083  # number data rows


def test_rbz():
    with omnio.open('tests/data/flights-3m.csv.gz', 'rbz') as fd:
        data = fd.read()
        assert type(data) is bytes
        assert len(data) == 5535530  # uncompressed file size


def test_rbj():
    with omnio.open('tests/data/flights-3m.csv.bz2', 'rbj') as fd:
        data = fd.read()
        assert type(data) is bytes
        assert len(data) == 5535530  # uncompressed file size


def test_w():
    path = 'tests/data/w.txt'
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


def test_wbz():
    path = 'tests/data/wbz.txt.gz'
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


def test_wbj():
    path = 'tests/data/wbj.txt.bz2'
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


def test_wtz():
    path = 'tests/data/wtz.txt.gz'
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
