import urllib

import boto3

UPLOAD_PART_SIZE = 5 * 1024**2


class S3Reader:
    def __init__(self, stream):
        self.stream = stream
        self.line_iter = _iter_lines(self, chunk_size=512)
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        self.close()

    def __iter__(self):
        self._ensure_open()

        return self

    def __next__(self):
        self._ensure_open()

        return next(self.line_iter)

    def _ensure_open(self):
        if self.closed:
            msg = 'I/O operation on a closed file'
            raise ValueError(msg)

    def close(self):
        self.closed = True

    def flush(self):  # pragma: no cover
        pass

    def readable(self):  # pragma: no cover
        return True

    def seekable(self):  # pragma: no cover
        return False

    def writable(self):  # pragma: no cover
        return False

    def read(self, size=None):
        self._ensure_open()

        data = self.stream.read(size)
        return data

    def seek(self, offset, whence=0):  # pragma: no cover
        raise NotImplementedError()


def _iter_lines(stream, chunk_size):
    pending = None
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break

        if pending is not None:
            chunk = pending + chunk

        lines = chunk.splitlines(keepends=True)

        # The last item in the list is typically an unfinished line
        # that needs to be completed with the next chunk. For
        # expediency, we treat it as incomplete until the next
        # chunk's splitlines() proves otherwise.
        pending = lines.pop()

        for line in lines:
            yield line

    if pending is not None:
        yield pending


class S3Writer:
    def __init__(self, s3, bucket, key):
        self.s3 = s3
        self.bucket = bucket
        self.key = key
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

    def flush(self):  # pragma: no cover
        pass

    def readable(self):  # pragma: no cover
        return False

    def seekable(self):  # pragma: no cover
        return False

    def writable(self):  # pragma: no cover
        return True

    def seek(self, offset, whence=None):  # pragma: no cover
        raise NotImplementedError()

    def write(self, data):
        self._ensure_open()

        self.buffer.extend(data)

        if len(self.buffer) > UPLOAD_PART_SIZE:  # pragma: no cover
            if self.multipart is None:
                self.multipart = self.s3.create_multipart_upload(
                        Bucket=self.bucket, Key=self.key)

            self._upload_part()


def open_(uri, mode):  # pragma: no cover
    parsed_uri = urllib.parse.urlparse(uri)
    bucket = parsed_uri.netloc
    key = parsed_uri.path.lstrip('/')

    s3 = boto3.client('s3')

    if 'x' in mode:
        msg = "s3 scheme doesn't support exclusive mode"
        raise ValueError(msg)

    if 'a' in mode:
        msg = "s3 scheme doesn't support append mode"
        raise ValueError(msg)

    if 'r' in mode:
        resp = s3.get_object(Bucket=bucket, Key=key)
        stream = resp['Body']

        return S3Reader(stream)

    if 'w' in mode:
        return S3Writer(s3, bucket, key)
