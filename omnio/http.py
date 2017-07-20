import io
import requests


class HTTPReader(io.IOBase):
    def __init__(self, resp):
        self.content_iter = resp.iter_content(chunk_size=512,
                                              decode_unicode=False)
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


def open_(uri, mode):  # pragma: no cover

    if 'x' in mode:
        msg = "http scheme doesn't support 'x' mode"
        raise ValueError(msg)

    if 'r' in mode:
        resp = requests.get(uri, stream=True)
        return HTTPReader(resp)

    if 'w' in mode:
        raise NotImplementedError()
