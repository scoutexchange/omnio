import io
import urllib

import boto3
import botocore
import botocore.exceptions


class S3Reader(io.IOBase):
    """Reader for streaming content from Amazon S3"""

    def __init__(self, stream):
        self.stream = stream

    def read(self, size=None):
        if self.closed:
            msg = 'I/O operation on a closed file'
            raise ValueError(msg)

        try:
            return self.stream.read(size)
        except botocore.exceptions.ReadTimeoutError as e:
            raise TimeoutError(e)

    def readable(self):  # pragma: no cover
        return True


class S3Writer(io.IOBase):
    """Writer for streaming content to Amazon S3"""

    def __init__(self, s3, bucket, key, upload_part_size):
        self.s3 = s3
        self.bucket = bucket
        self.key = key
        self.upload_part_size = upload_part_size
        self.buffer = bytearray()
        self.multipart = None
        self.parts = []

    def _upload_part(self):  # pragma: no cover
        if not self.buffer:
            return

        size = self.upload_part_size
        data = self.buffer[:size]

        part = self.s3.upload_part(
            Bucket=self.bucket,
            Key=self.key,
            PartNumber=len(self.parts) + 1,
            UploadId=self.multipart['UploadId'],
            Body=data,
        )
        self.parts.append(part)

        self.buffer = self.buffer[size:]

    def close(self):  # pragma: no cover
        if self.closed:
            return

        super(S3Writer, self).close()

        if not self.multipart:
            self.s3.put_object(Bucket=self.bucket, Key=self.key, Body=self.buffer)
            return

        self._upload_part()
        part_info = {
            'Parts': [
                {'PartNumber': i + 1, 'ETag': part['ETag']}
                for i, part in enumerate(self.parts)
            ]
        }
        self.s3.complete_multipart_upload(
            Bucket=self.bucket,
            Key=self.key,
            UploadId=self.multipart['UploadId'],
            MultipartUpload=part_info,
        )

    def write(self, data):
        if self.closed:
            msg = 'I/O operation on a closed file'
            raise ValueError(msg)

        # ensure that data is bytes-like
        try:
            memoryview(data)
        except TypeError:
            raise TypeError(
                f"a bytes-like object is required, not '{type(data).__name__}'"
            ) from None

        self.buffer.extend(data)

        if len(self.buffer) > self.upload_part_size:  # pragma: no cover
            if self.multipart is None:
                self.multipart = self.s3.create_multipart_upload(
                    Bucket=self.bucket, Key=self.key
                )

            self._upload_part()

    def writable(self):  # pragma: no cover
        return True


def _open(uri, mode, config):  # pragma: no cover
    parsed_uri = urllib.parse.urlparse(uri)
    bucket = parsed_uri.netloc
    key = parsed_uri.path.lstrip('/')

    args = config["s3"]["boto_client_config_args"]
    kwargs = config["s3"]["boto_client_config_kwargs"]
    boto_config = botocore.client.Config(*args, **kwargs)
    s3 = boto3.client('s3', config=boto_config)

    if any(c in mode for c in 'ax+'):
        msg = "s3 scheme doesn't support '{}' mode".format(mode)
        raise ValueError(msg)

    if 'r' in mode:
        try:
            resp = s3.get_object(Bucket=bucket, Key=key)
        except botocore.errorfactory.ClientError as client_error:
            if client_error.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError(client_error)
            raise
        except botocore.exceptions.EndpointConnectionError as e:
            raise ConnectionError(e)

        stream = resp['Body']
        return S3Reader(stream)

    if 'w' in mode:
        upload_part_size = config["s3"]["upload_part_size"]
        return S3Writer(s3, bucket, key, upload_part_size)
