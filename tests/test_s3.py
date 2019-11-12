import io
import os

import botocore.stub
import botocore.response
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

        with omnio.s3.S3Writer(s3, 'my-bucket', 'my-key') as writer:
            writer.write(data)

        stubber.assert_no_pending_responses()


def test_write_closed():
    response = {}
    expected_params = {'Bucket': 'my-bucket', 'Key': 'my-key', 'Body': bytearray()}
    s3 = botocore.session.get_session().create_client('s3')
    f = omnio.s3.S3Writer(s3, 'my-bucket', 'my-key')
    with botocore.stub.Stubber(s3) as stubber:
        stubber.add_response('put_object', response, expected_params)
        f.close()

    with pytest.raises(ValueError):
        f.write(b'')
