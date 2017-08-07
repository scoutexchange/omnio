# omnio

*Python library for opening URIs as streaming file-like objects*

This library provides the `omnio.open()` function with an interface very
similar to that of the built in Python `open` function.  The difference is
that while Python's `open` operates only on local filesystem paths, `omnio`
accepts URIs as well.

In addition, it supports compression and decompression of streams with gzip
or bz2.

It currently supports `file`, `http`, and `s3` URIs, though it may be
expanded to support additional schemes in the future.

## Features

* API is a superset of Python 3's built-in open() function
* Based on Python 3 `io` module
* Gzip and bzip2 support both for reading and writing
* Local file support using standard library
* HTTP support using `requests`
* S3 support using `boto3`

## Examples

Exactly like the built-in `open()`, you can write `str` text to a file as
'utf-8' encoded bytes.

    with omnio.open('example.txt', 'wt', encoding='utf-8') as f:
        f.write('This text will be encoded as utf-8. ')
        f.write('Actually, 'utf-8' is the default encoding, so we ')
        f.write('could have skipped that argument in this case.')

You can also compress the stream with gzip by adding 'z' to the mode.

    with omnio.open('example.txt.gz', 'wtz') as f:
        f.write("This text will be gzip compressed because 'z' was specified.\n")
        f.writer("bz2 is also supported by adding 'j'.")

The 'z' and 'j' flags also apply to 'r' modes to decompress the stream.

    with omnio.open('example.txt.gz', 'rtz') as f:
        for line in f:
            print line

You can stream NASA's Meteorite Landings CSV dataset into memory by supplying
the `omnio`'s file-like object to Python's standard library `csv` module.

    import csv
    import omnio

    with omnio.open('https://data.nasa.gov/api/views/gh4g-9sfh/rows.csv', 'rt') as f:
        reader = csv.reader(f)
        data = list(reader)

The object `omnio.open()` returns can generally be used with 3rd party
libraries that accept files. Here we seamlessly load a gzipped CSV galaxy
classification dataset into a `pandas` dataframe.

    import pandas
    import omnio

    with omnio.open('http://galaxy-zoo-1.s3.amazonaws.com/GalaxyZoo1_DR_table2.csv.gz', 'rbz') as f:
        df = pandas.read_csv(f)

We can also read and write from Amazon S3.

    import omnio

    data = b"These are bytes. We can write them in 'b' mode."
    with omnio.open('s3://my-bucket/my-key', 'wb') as f:
        f.write(data)

Binary mode is the default. If we want to instead write text we need to
explicitly specify 't':

    text = 'This is unencoded unicode text but we can specify how to encode it.'
    with omnio.open('s3://my-bucket/my-key', 'wt', encoding='ascii') as f:
        f.write(text)
