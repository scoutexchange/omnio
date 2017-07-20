import requests


class HTTPReader:
    def __init__(self, resp):
        self.content_iter = resp.iter_content(chunk_size=512,
                                              decode_unicode=False)
        self.line_iter = _iter_lines(self.content_iter)
        self.buffer = bytearray()
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

    def flush(self):
        pass

    def read(self, size=None):
        self._ensure_open()

        while True:
            if size is not None and len(self.buffer) >= size:
                break

            try:
                chunk = next(self.content_iter)
            except StopIteration:
                break
            else:
                self.buffer.extend(chunk)

        data = self.buffer[:size]
        self.buffer = self.buffer[size:]

        return data

    def readable(self):
        return True

    def seekable(self):
        return False

    def writable(self):
        return False

    def seek(self, offset, whence=0):  # pragma: no cover
        raise NotImplementedError()


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


def open_(uri, mode):  # pragma: no cover

    if 'x' in mode:
        msg = "http scheme doesn't support 'x' mode"
        raise ValueError(msg)

    if 'r' in mode:
        resp = requests.get(uri, stream=True)
        return HTTPReader(resp)

    if 'w' in mode:
        raise NotImplementedError()
