import os
import responses

import pytest

import omnio

ascii_text = """
                .                                            .
     *   .                  .              .        .   *          .
  .         .                     .       .           .      .        .
        o                             .                   .
         .              .                  .           .
          0     .
                 .          .                 ,                ,    ,
 .          \          .                         .
      .      \   ,
   .          o     .                 .                   .            .
     .         \                 ,             .                .
               #\##\#      .                              .        .
             #  #O##\###                .                        .
   .        #*#  #\##\###                       .                     ,
        .   ##*#  #\##\##               .                     .
      .      ##*#  #o##\#         .                             ,       .
          .     *#  #\#     .                    .             .          ,
                      \          .                         .
____^/\___^--____/\____O______________/\/\---/\___________---______________
   /\^   ^  ^    ^                  ^^ ^  '\ ^          ^       ---
         --           -            --  -      -         ---  __       ^
   --  __                      ___--  ^  ^                         --  __
"""

iso_8859_text = (
    "Sed ut perspiciatis unde omnis iste natus error sit voluptatem "
    "accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae "
    "ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt "
    "explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut "
    "odit aut fugit, sed quia consequuntur magni dolores eos qui ratione "
    "voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum "
    "quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam "
    "eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat "
    "voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam "
    "corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur?"
)

utf8_text = """Οὐχὶ ταὐτὰ παρίσταταί μοι γιγνώσκειν, ὦ ἄνδρες ᾿Αθηναῖοι,
ὅταν τ᾿ εἰς τὰ πράγματα ἀποβλέψω καὶ ὅταν πρὸς τοὺς
λόγους οὓς ἀκούω· τοὺς μὲν γὰρ λόγους περὶ τοῦ
τιμωρήσασθαι Φίλιππον ὁρῶ γιγνομένους, τὰ δὲ πράγματ᾿
εἰς τοῦτο προήκοντα,  ὥσθ᾿ ὅπως μὴ πεισόμεθ᾿ αὐτοὶ
πρότερον κακῶς σκέψασθαι δέον. οὐδέν οὖν ἄλλο μοι δοκοῦσιν
οἱ τὰ τοιαῦτα λέγοντες ἢ τὴν ὑπόθεσιν, περὶ ἧς βουλεύεσθαι,
οὐχὶ τὴν οὖσαν παριστάντες ὑμῖν ἁμαρτάνειν. ἐγὼ δέ, ὅτι μέν
ποτ᾿ ἐξῆν τῇ πόλει καὶ τὰ αὑτῆς ἔχειν ἀσφαλῶς καὶ Φίλιππον
τιμωρήσασθαι, καὶ μάλ᾿ ἀκριβῶς οἶδα· ἐπ᾿ ἐμοῦ γάρ, οὐ πάλαι
γέγονεν ταῦτ᾿ ἀμφότερα· νῦν μέντοι πέπεισμαι τοῦθ᾿ ἱκανὸν
προλαβεῖν ἡμῖν εἶναι τὴν πρώτην, ὅπως τοὺς συμμάχους
σώσομεν. ἐὰν γὰρ τοῦτο βεβαίως ὑπάρξῃ, τότε καὶ περὶ τοῦ
τίνα τιμωρήσεταί τις καὶ ὃν τρόπον ἐξέσται σκοπεῖν· πρὶν δὲ
τὴν ἀρχὴν ὀρθῶς ὑποθέσθαι, μάταιον ἡγοῦμαι περὶ τῆς
τελευτῆς ὁντινοῦν ποιεῖσθαι λόγον."""


@responses.activate
def test_open_rt_ascii():
    uri = 'http://example.com/example'
    data = ascii_text.encode('ascii')
    responses.add(responses.GET, uri, body=data, status=200,
                  content_type='text/plain; charset=ASCII')

    with omnio.open(uri, 'rt') as infile:
        assert infile.read() == ascii_text


@responses.activate
def test_open_rt_iso_8859_1():
    uri = 'http://example.com/example'
    data = iso_8859_text.encode('iso-8859-1')
    responses.add(responses.GET, uri, body=data, status=200,
                  content_type='text/plain; charset=ISO-8859-1')

    with omnio.open(uri, 'rt') as infile:
        assert infile.read() == iso_8859_text


@responses.activate
def test_open_rt_utf8():
    uri = 'http://example.com/example'
    data = utf8_text.encode('utf-8')
    responses.add(responses.GET, uri, body=data, status=200,
                  content_type='text/plain; charset=UTF-8')

    with omnio.open(uri, 'rt') as infile:
        assert infile.read() == utf8_text


@responses.activate
def test_read_chunk():
    uri = 'http://example.com/example'
    data = os.urandom(1024)
    responses.add(responses.GET, uri, body=data, status=200)
    with omnio.open(uri, 'rb') as infile:
        chunk = infile.read(1000)
        assert len(chunk) == 1000
        assert chunk == data[:1000]
        chunk = infile.read(1000)
        assert len(chunk) == 24
        assert chunk == data[1000:]


@responses.activate
def test_iter():
    uri = 'http://example.com/example'
    data = utf8_text.encode('utf-8')
    responses.add(responses.GET, uri, body=data, status=200,
                  content_type='text/plain; charset=UTF-8')

    expect_first = 'Οὐχὶ ταὐτὰ παρίσταταί μοι γιγνώσκειν, ὦ ἄνδρες ' \
        '᾿Αθηναῖοι,\n'.encode('utf-8')
    expect_last = 'τελευτῆς ὁντινοῦν ποιεῖσθαι λόγον.'.encode('utf-8')

    with omnio.open(uri, 'rb') as infile:
        lines = list(infile)
        assert len(lines) == 16
        assert lines[0] == expect_first
        assert lines[-1] == expect_last


@responses.activate
def test_closed():
    uri = 'http://example.com/example'
    data = b'foo bar baz'
    responses.add(responses.GET, uri, body=data, status=200)
    f = omnio.open(uri, 'rb')
    f.close()

    # none of these operations are allowed on a closed file
    with pytest.raises(ValueError):
        f.read()
    with pytest.raises(ValueError):
        next(f)
    with pytest.raises(ValueError):
        iter(f)
