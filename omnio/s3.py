import io
import urllib

import boto3

UPLOAD_PART_SIZE = 5 * 1024**2


class S3Reader(io.IOBase):
    def __init__(self, stream):
        self.stream = stream

    def read(self, size=None):
        if self.closed:
            msg = 'I/O operation on a closed file'
            raise ValueError(msg)

        return self.stream.read(size)

    def readable(self):  # pragma: no cover
        return True


class S3Writer(io.IOBase):
    def __init__(self, s3, bucket, key):
        self.s3 = s3
        self.bucket = bucket
        self.key = key
        self.buffer = bytearray()
        self.multipart = None
        self.parts = []

    def _upload_part(self):  # pragma: no cover
        if not self.buffer:
            return

        data = self.buffer[:UPLOAD_PART_SIZE]

        part = self.s3.upload_part(Bucket=self.bucket, Key=self.key,
                                   PartNumber=len(self.parts)+1,
                                   UploadId=self.multipart['UploadId'],
                                   Body=data)
        self.parts.append(part)

        self.buffer = self.buffer[UPLOAD_PART_SIZE:]

    def close(self):  # pragma: no cover
        if self.closed:
            return

        super(S3Writer, self).close()

        if not self.multipart:
            self.s3.put_object(Bucket=self.bucket, Key=self.key,
                               Body=self.buffer)
            return

        self._upload_part()
        part_info = {
            'Parts': [{'PartNumber': i+1, 'ETag': part['ETag']}
                      for i, part in enumerate(self.parts)]
        }
        self.s3.complete_multipart_upload(Bucket=self.bucket, Key=self.key,
                                          UploadId=self.multipart['UploadId'],
                                          MultipartUpload=part_info)

    def write(self, data):
        if self.closed:
            msg = 'I/O operation on a closed file'
            raise ValueError(msg)

        self.buffer.extend(data)

        if len(self.buffer) > UPLOAD_PART_SIZE:  # pragma: no cover
            if self.multipart is None:
                self.multipart = self.s3.create_multipart_upload(
                        Bucket=self.bucket, Key=self.key)

            self._upload_part()

    def writable(self):  # pragma: no cover
        return True


def _open(uri, mode):  # pragma: no cover
    parsed_uri = urllib.parse.urlparse(uri)
    bucket = parsed_uri.netloc
    key = parsed_uri.path.lstrip('/')

    s3 = boto3.client('s3')

    if any(c in mode for c in 'ax+'):
        msg = "s3 scheme doesn't support '{}' mode".format(mode)
        raise ValueError(msg)

    if 'r' in mode:
        resp = s3.get_object(Bucket=bucket, Key=key)
        stream = resp['Body']

        return S3Reader(stream)

    if 'w' in mode:
        return S3Writer(s3, bucket, key)
