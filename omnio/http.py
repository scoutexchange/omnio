from io import BytesIO, StringIO
import os

import requests


class Reader:
    def __init__(self, resp, decode_unicode):
        self.decode_unicode = decode_unicode
        self.content_iter = resp.iter_content(chunk_size=512,
                                              decode_unicode=decode_unicode)
        self.line_iter = _iter_lines(self.content_iter)
        self.buffer = _make_buffer(decode_unicode)
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

    def read(self, size=None):
        self._ensure_open()

        while True:
            self.buffer.seek(0, os.SEEK_END)
            if size is not None and self.buffer.tell() >= size:
                break

            try:
                chunk = next(self.content_iter)
            except StopIteration:
                break
            else:
                self.buffer.write(chunk)

        self.buffer.seek(0)
        data = self.buffer.read(size)
        pending = self.buffer.read()
        self.buffer = _make_buffer(self.decode_unicode, pending)

        return data

    def readlines(self):
        return list(self)

    def seek(self, offset, whence=0):  # pragma: no cover
        raise NotImplementedError()


def _make_buffer(decode_unicode, data=None):
    return StringIO(data) if decode_unicode else BytesIO(data)


def _iter_lines(content_iter):
    pending = None
    for chunk in content_iter:
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


def open_(uri, mode, encoding):  # pragma: no cover

    # http.Reader relies on the Content-Type header for the encoding.
    # It's possible we could support this in the future as an
    # override or a fallback.
    if encoding is not None:
        msg = "http scheme doesn't support encoding argument"
        raise ValueError(msg)

    if 'r' in mode:
        resp = requests.get(uri, stream=True)
        decode_unicode = 'b' not in mode
        return Reader(resp, decode_unicode)

    if 'w' in mode:
        raise NotImplementedError()
