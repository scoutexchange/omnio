import io
import os

import botocore.exceptions
import botocore.response
import botocore.stub
import pytest

import omnio


def test_read_binary():
    data = os.urandom(1000)
    stream = io.BytesIO(data)

    with omnio.s3.S3Reader(stream) as reader:
        assert reader.read() == data


def test_read_n_binary():
    data = b'one\ntwo\nthree'
    stream = io.BytesIO(data)

    with omnio.s3.S3Reader(stream) as reader:
        assert reader.read(5) == data[:5]


def test_read_timeout_error():
    class Stream(io.BytesIO):
        def read(self, *args, **kwargs):
            raise botocore.exceptions.ReadTimeoutError(endpoint_url="test/")

    with omnio.s3.S3Reader(Stream()) as reader:
        with pytest.raises(TimeoutError):
            reader.read()


def test_read_connection_error(monkeypatch):
    class Client:
        def __init__(self, *args, **kwargs):
            pass

        def get_object(self, Bucket=None, Key=None):
            raise botocore.exceptions.EndpointConnectionError(endpoint_url="test/")

    monkeypatch.setattr("boto3.client", Client)

    with pytest.raises(ConnectionError):
        with omnio.open("s3://bucket/key"):
            pass


def test_iter():
    data = b'one\ntwo\nthree four'
    stream = io.BytesIO(data)

    with omnio.s3.S3Reader(stream) as reader:
        assert next(reader) == b'one\n'
        assert next(reader) == b'two\n'
        assert next(reader) == b'three four'


def test_iter_lines():
    lines = [b'0' * 512 + b'\n', b'1' * 666 + b'\n', b'2' * 256]
    stream = io.BytesIO(b''.join(lines))

    with omnio.s3.S3Reader(stream) as reader:
        for expected, data in zip(lines, reader):
            print(len(data), len(expected))
            assert data == expected


def test_closed():
    data = b'one\ntwo\nthree four'
    stream = io.BytesIO(data)
    f = omnio.s3.S3Reader(stream)
    f.close()

    # none of these operations are allowed on a closed file
    with pytest.raises(ValueError):
        f.read()
    with pytest.raises(ValueError):
        next(f)
    with pytest.raises(ValueError):
        iter(f)


def test_write():
    data = b'one\ntwo\nthree\nfour five'

    response = {}
    expected_params = {'Bucket': 'my-bucket', 'Key': 'my-key', 'Body': bytearray(data)}

    s3 = botocore.session.get_session().create_client('s3')
    with botocore.stub.Stubber(s3) as stubber:
        stubber.add_response('put_object', response, expected_params)

        with omnio.s3.S3Writer(s3, 'my-bucket', 'my-key', 512) as writer:
            writer.write(data)

        stubber.assert_no_pending_responses()


def test_write_closed():
    response = {}
    expected_params = {'Bucket': 'my-bucket', 'Key': 'my-key', 'Body': bytearray()}
    s3 = botocore.session.get_session().create_client('s3')
    f = omnio.s3.S3Writer(s3, 'my-bucket', 'my-key', 512)
    with botocore.stub.Stubber(s3) as stubber:
        stubber.add_response('put_object', response, expected_params)
        f.close()

    with pytest.raises(ValueError):
        f.write(b'')
