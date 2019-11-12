import io
import requests


class HTTPReader(io.IOBase):
    """Reader for HTTP response content"""

    def __init__(self, resp, chunk_size):
        self.content_iter = resp.iter_content(
            chunk_size=chunk_size, decode_unicode=False
        )
        self.buffer = bytearray()

    def read(self, size=None):
        if self.closed:
            msg = 'I/O operation on a closed file'
            raise ValueError(msg)

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

        return bytes(data)

    def readable(self):
        return True


def _open(uri, mode, config):

    if any(c in mode for c in 'wax+'):  # pragma: no cover
        msg = "http scheme doesn't support '{}' mode".format(mode)
        raise NotImplementedError(msg)

    if 'r' in mode:
        chunk_size = config["http"]["iter_content_chunk_size"]
        resp = requests.get(uri, stream=True)
        return HTTPReader(resp, chunk_size)
