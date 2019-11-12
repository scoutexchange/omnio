import os
import responses

import pytest

import omnio


def _load_test_data(encoding):
    path = 'tests/data/{}.txt'.format(encoding)
    with open(path, 'rb') as fd:
        return fd.read()


@responses.activate
def test_open_rt_ascii():
    uri = 'http://example.com/example'
    data = _load_test_data('ascii')
    responses.add(
        responses.GET,
        uri,
        body=data,
        status=200,
        content_type='text/plain; charset=ASCII',
    )

    with omnio.open(uri, 'rt') as infile:
        assert infile.read() == data.decode('ascii')


@responses.activate
def test_open_rt_iso_8859_1():
    uri = 'http://example.com/example'
    data = _load_test_data('iso-8859-1')
    responses.add(
        responses.GET,
        uri,
        body=data,
        status=200,
        content_type='text/plain; charset=ISO-8859-1',
    )

    with omnio.open(uri, 'rt') as infile:
        assert infile.read() == data.decode('iso-8859-1')


@responses.activate
def test_open_rt_utf8():
    uri = 'http://example.com/example'
    data = _load_test_data('utf-8')
    responses.add(
        responses.GET,
        uri,
        body=data,
        status=200,
        content_type='text/plain; charset=UTF-8',
    )

    with omnio.open(uri, 'rt') as infile:
        assert infile.read() == data.decode('utf-8')


@responses.activate
def test_read_chunk():
    uri = 'http://example.com/example'
    data = os.urandom(1024)
    responses.add(responses.GET, uri, body=data, status=200)
    with omnio.open(uri, 'rb') as infile:
        chunk = infile.read(1000)
        assert len(chunk) == 1000
        assert chunk == data[:1000]
        chunk = infile.read(1000)
        assert len(chunk) == 24
        assert chunk == data[1000:]


@responses.activate
def test_iter():
    uri = 'http://example.com/example'
    data = _load_test_data('utf-8')
    responses.add(
        responses.GET,
        uri,
        body=data,
        status=200,
        content_type='text/plain; charset=UTF-8',
    )

    expect_first = (
        'Οὐχὶ ταὐτὰ παρίσταταί μοι γιγνώσκειν, ὦ ἄνδρες ' '᾿Αθηναῖοι,\n'.encode('utf-8')
    )
    expect_last = 'τελευτῆς ὁντινοῦν ποιεῖσθαι λόγον.'.encode('utf-8')

    with omnio.open(uri, 'rb') as infile:
        lines = list(infile)
        assert len(lines) == 16
        assert lines[0] == expect_first
        assert lines[-1] == expect_last


@responses.activate
def test_closed():
    uri = 'http://example.com/example'
    data = b'foo bar baz'
    responses.add(responses.GET, uri, body=data, status=200)
    f = omnio.open(uri, 'rb')
    f.close()

    # none of these operations are allowed on a closed file
    with pytest.raises(ValueError):
        f.read()
    with pytest.raises(ValueError):
        next(f)
    with pytest.raises(ValueError):
        iter(f)
