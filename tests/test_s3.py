import io
import os

import botocore.exceptions
import botocore.response
import botocore.stub
import boto3
import moto
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


def test_write_not_utf8():
    s3 = botocore.session.get_session().create_client('s3')
    with botocore.stub.Stubber(s3) as stubber:

        data = b'\037\213'
        stubber.add_response('put_object', {})
        with omnio.s3.S3Writer(s3, 'my-bucket', 'my-key', 512) as writer:
            writer.write(data)

        stubber.assert_no_pending_responses()


def test_write_not_bytes():
    s3 = botocore.session.get_session().create_client('s3')
    with botocore.stub.Stubber(s3) as stubber:

        # various data that isn't bytes-like
        for data in ["foo", 42, []]:
            stubber.add_response('put_object', {})
            with pytest.raises(TypeError):
                with omnio.s3.S3Writer(s3, 'my-bucket', 'my-key', 512) as writer:
                    writer.write(data)

        stubber.assert_no_pending_responses()


@moto.mock_s3
def test_iglob():
    bucket = "mock-bucket"
    s3 = boto3.resource('s3')
    s3.create_bucket(Bucket=bucket)

    for fn in [
        "one.txt.gz",
        "two.txt.gz",
        "three.txt.gz",
        "prefix/four.txt.gz",
        "ascii.txt",
    ]:
        obj = s3.Object(bucket, fn)
        with open(f"tests/data/{fn}", "rb") as fd:
            content = fd.read()
            obj.put(Body=content)

    lines = set()
    for uri in omnio.glob.iglob(f"s3://{bucket}/*.txt.gz"):
        with omnio.open(uri, "rtz") as fd:
            for line in fd:
                lines.add(line.rstrip("\n"))

    assert lines == {
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
    }


@moto.mock_s3
def test_iglob_recursive():
    bucket = "mock-bucket"
    s3 = boto3.resource('s3')
    s3.create_bucket(Bucket=bucket)

    for fn in [
        "one.txt.gz",
        "two.txt.gz",
        "three.txt.gz",
        "prefix/four.txt.gz",
        "ascii.txt",
    ]:
        obj = s3.Object(bucket, fn)
        with open(f"tests/data/{fn}", "rb") as fd:
            content = fd.read()
            obj.put(Body=content)

    lines = set()
    for uri in omnio.glob.iglob(f"s3://{bucket}/*.txt.gz", recursive=True):
        with omnio.open(uri, "rtz") as fd:
            for line in fd:
                lines.add(line.rstrip("\n"))

    assert lines == {
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
        "ten",
        "eleven",
        "twelve",
    }
