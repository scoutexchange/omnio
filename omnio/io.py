class Reader:
    def __init__(self, stream, encoding):
        self.stream = stream
        self.encoding = encoding
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

    def read(self, size=None):
        self._ensure_open()

        data = self.stream.read(size)
        if self.encoding:
            data = data.decode(self.encoding)
        return data

    def readlines(self):
        return list(self)

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
