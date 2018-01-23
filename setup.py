import omnio

from distutils import core


classifiers = ['Development Status :: 5 - Production/Stable',
               'Intended Audience :: Developers',
               'Programming Language :: Python',
               'License :: OSI Approved :: MIT License',
               'Natural Language :: English',
               'Operating System :: OS Independent',
               'Programming Language :: Python',
               'Programming Language :: Python :: 3',
               'Programming Language :: Python :: Implementation',
               'Programming Language :: Python :: Implementation :: CPython',
               'Topic :: Internet :: WWW/HTTP',
               'Topic :: Software Development :: Libraries :: Python Modules',
               'Topic :: Utilities']

version = omnio.__version__
url = "https://github.com/scoutexchange/omnio"
tarball_url = "%s/tarball/v%s" % (url, version)


def readme():
    with open("README.md", "r") as infile:
        return infile.read()


core.setup(name='omnio',
           version=version,
           description='Streaming file-like resources',
           long_description=readme(),
           packages=['omnio'],
           install_requires=['boto3', 'requests'],
           author='Bob Green',
           author_email='rgreen@goscoutgo.com',
           keywords = 'open file file-like streaming s3 boto boto3 http gzip bz2 compression',
           url=url,
           download_url=tarball_url,
           license='MIT',
           classifiers=classifiers)
