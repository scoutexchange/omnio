import botocore.stub
import botocore.response
import pytest

import omnio


def test_write():
    data = b'one\ntwo\nthree\nfour five'

    response = {}
    expected_params = {'Bucket': 'my-bucket', 'Key': 'my-key',
                       'Body': bytearray(data)}

    s3 = botocore.session.get_session().create_client('s3')
    with botocore.stub.Stubber(s3) as stubber:
        stubber.add_response('put_object', response, expected_params)

        with omnio.s3.Writer(s3, 'my-bucket', 'my-key', None) as writer:
            writer.write(data)

        stubber.assert_no_pending_responses()


def test_write_str():
    data = 'one\ntwo\nthree\nfour five'

    response = {}
    expected_params = {'Bucket': 'my-bucket', 'Key': 'my-key',
                       'Body': bytearray(data, encoding='utf-8')}

    s3 = botocore.session.get_session().create_client('s3')
    with botocore.stub.Stubber(s3) as stubber:
        stubber.add_response('put_object', response, expected_params)

        with omnio.s3.Writer(s3, 'my-bucket', 'my-key', 'utf-8') as writer:
            writer.write(data)

        stubber.assert_no_pending_responses()


def test_write_closed():
    response = {}
    expected_params = {'Bucket': 'my-bucket', 'Key': 'my-key',
                       'Body': bytearray()}
    s3 = botocore.session.get_session().create_client('s3')
    f = omnio.s3.Writer(s3, 'my-bucket', 'my-key', encoding=None)
    with botocore.stub.Stubber(s3) as stubber:
        stubber.add_response('put_object', response, expected_params)
        f.close()

    with pytest.raises(ValueError):
        f.write(b'')
