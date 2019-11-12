# omnio

*Python 3 library for opening URIs as streaming file-like objects*

This library provides the `omnio.open()` function with an interface very
similar to that of the built in Python `open` function.  The difference is
that while Python's `open` operates only on local filesystem paths, `omnio`
accepts URIs as well.

It currently supports `file`, `http`, and `s3` URIs, though it may be
expanded to support additional schemes in the future.

In addition, it supports compression and decompression of streams with gzip
or bz2.

## Features

* API is a superset of Python 3's built-in open() function
* Based on Python 3 `io` module
* Gzip and bzip2 support both for reading and writing
* Local file support using standard library
* HTTP support using `requests`
* S3 support using `boto3`

## Examples

Read a local binary file:

    >>> with omnio.open('example.bin', 'r') as f:
    >>>     data = f.read()

Read a local text file:

    >>> with omnio.open('example.txt', 'rt') as f:
    >>>     text = f.read()

Read a text file from the web:

    >>> with omnio.open('https://example.com/example.txt', 'rt') as f:
    >>>     text = f.read()

Read a gzipped text file from the web, uncompressing on the fly:

    >>> with omnio.open('https://example.com/example.txt.gz', 'rtz') as f:
    >>>     text = f.read()

Read a text file from s3:

    >>> with omnio.open('s3://my-bucket/my-key', 'rt') as f:
    >>>     text = f.read()

Write a megabyte of random data to s3, compressing with bzip2:

    >>> import os
    >>> data = os.urandom(1024**2)
    >>> with omnio.open('s3://my-bucket/my-key', 'wbj') as f:
    >>>     f.write(data)

Read a bzip2 compressed csv file into a list of data rows:

    >>> import csv
    >>> with omnio.open('data/example_data.csv.bz2', 'rtj') as f:
    >>>     reader = csv.reader(f)
    >>>     data = list(reader)


## API

The omnio API consists of a single function intended to be referenced as
`omnio.open()`. This function API is designed to mimic Python 3's built-in
`open()` as much as possible, and should normally be able to be used as a
drop-in replacement.

_Signature:_

`omnio.open(uri, mode='rb', encoding=None, errors=None, newline=None)`

_Returns:_

A file-like object whose type depends on the scheme and the mode.

_Parameters:_
  * _uri_ -- URI or local path. Supported URI schemes are `file`,
  `http`, and `s3`. Local paths may be specified by as ordinary path
  strings.

  * _mode_ -- Optional string that specifies the mode in which the
  file is opened. It defaults to 'rb' which means open for reading
  in binary mode. Supported modes are documented below.

_Modes:_

| Character | Meaning |
| --------- | ------- |
| 'r'       | open for reading (default)                  |
| 'w'       | open for writing, truncating the file first |
| 'b'       | binary mode (default)                       |
| 't'       | text mode                                   |
| 'z'       | use gzip compression                        |
| 'j'       | use bzip2 compression                       |

These characters can be composed into valid modes. Binary mode is
always the default, so some mode specifications are equivalent.
The complete list of supported modes are as follows:

| Mode        | Meaning |
| ----------- | ------- |
| 'r', 'rb'   | read bytes                                          |
| 'rt'        | read and decode to unicode                          |
| 'rz', 'rbz' | read, decompressing gzip to bytes                   |
| 'rj', 'rbj' | read, decompressing bzip2 to bytes                  |
| 'rtz'       | read, decompress gzip to bytes, decode to unicode   |
| 'rtj'       | read, decompress bzip2 to bytes, decode to unicode  |
| 'w', 'wb'   | write bytes                                         |
| 'wt'        | write unicode, encoding to bytes                    |
| 'wz', 'wbz' | write bytes, compress with gzip                     |
| 'wj', 'wbj' | write bytes, compress with bzip2                    |
| 'wtz'       | write unicode, encode to bytes, compress with gzip  |
| 'wtj'       | write unicode, encode to bytes, compress with bzip2 |

_Some keyword arguments may be applicable to only certain modes. For
example, `encoding` only applies to 't' (text) modes._

_Some schemes may not support some modes.  For example, the http
scheme currently does not support any 'w' (write) modes._


## Configuration

The `omnio.open` function accepts an optional `config` parameter. This allows
for specifying scheme-specific configuration.

The `default_config()` method returns a config dictionary with all supported
keys defined along with their default values.

    >>> import omnio
    >>> omnio.default_config()
    {'file': {}, 'http': {'content_iter_chunk_size': 512}, 's3': {'upload_part_size': 5242880, 'boto_client_config_args': [], 'boto_client_config_kwargs': {}}}

To specify alternate values for these parameters, instantiate a default
config, update the dict with the desired values and pass it as a keyword arg
to the `omnio.open()` function.

    >>> config = omnio.default_config()
    >>> config["s3"]["boto_client_config_kwargs"] = {"read_timeout": 600}
    >>> with omnio.open("s3://my-bucket/my-key", "rt", config=config) as fd:
        fd.read()
