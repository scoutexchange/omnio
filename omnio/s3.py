import locale
import urllib

import boto3

from omnio import io

UPLOAD_PART_SIZE = 5 * 1024**2


class Writer:
    def __init__(self, s3, bucket, key, encoding):
        self.s3 = s3
        self.bucket = bucket
        self.key = key
        self.encoding = encoding
        self.buffer = bytearray()
        self.multipart = None
        self.parts = []
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        return self.close()

    def _ensure_open(self):
        if self.closed:
            msg = 'I/O operation on a closed file'
            raise ValueError(msg)

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

        self.closed = True

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

    def seek(self, offset, whence=None):  # pragma: no cover
        raise NotImplementedError()

    def write(self, data):
        self._ensure_open()

        if self.encoding:
            data = data.encode(self.encoding)

        self.buffer.extend(data)

        if len(self.buffer) > UPLOAD_PART_SIZE:  # pragma: no cover
            if self.multipart is None:
                self.multipart = self.s3.create_multipart_upload(
                        Bucket=self.bucket, Key=self.key)

            self._upload_part()


def open_(uri, mode, encoding):  # pragma: no cover
    parsed_uri = urllib.parse.urlparse(uri)
    bucket = parsed_uri.netloc
    key = parsed_uri.path.lstrip('/')

    s3 = boto3.client('s3')

    if 'b' not in mode and encoding is None:
        encoding = locale.getpreferredencoding(do_setlocale=False)

    if 'r' in mode:
        resp = s3.get_object(Bucket=bucket, Key=key)
        stream = resp['Body']

        return io.Reader(stream, encoding)

    if 'w' in mode:
        return Writer(s3, bucket, key, encoding)
