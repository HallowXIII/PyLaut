from pylaut.language.phonology import word
from pylaut.pylautlang import parser

import pytest

@pytest.fixture
def wf():
    return word.WordFactory()

def test_simple_unconditional(wf):
    sc = parser.compile("CHANGE BEGIN /a/ -> /e/ END")[0]
    w = wf.make_word("'at.na")
    nw = sc.apply(w)
    assert repr(nw) == "/'et.ne/"


def test_multiple_unconditional(wf):
    sc = parser.compile("CHANGE BEGIN {/b/,/d/,/ɡ/} -> {/β/,/ð/,/ɣ/} END")[0]
    w = wf.make_word("ba'ɡo.dam")
    nw = sc.apply(w)
    assert repr(nw) == "/βa.'ɣo.ðam/"


def test_change_feature(wf):
    sc = parser.compile("CHANGE BEGIN [+sibilant] -> [+voice] END")[0]
    w = wf.make_word("ma'sa.la")
    nw = sc.apply(w)
    assert repr(nw) == "/ma.'za.la/"


def test_replace_by_feature(wf):
    sc = parser.compile("CHANGE BEGIN [+sibilant] -> /h/ END")[0]
    w = wf.make_word("ma'sa.la")
    nw = sc.apply(w)
    assert repr(nw) == "/ma.'ha.la/"


def test_basic_conditional_sound_change_with_relexp(wf):
    sc = parser.compile("CHANGE BEGIN /a/ -> /e/ | _[+front] END")[0]
    w = wf.make_word("ko'raj.ka")
    nw = sc.apply(w)
    assert repr(nw) == "/ko.'rej.ka/"


def test_simple_conditional_with_relexp(wf):
    sc = parser.compile("""
    CHANGE BEGIN
      /a/ => /e/ | _[+front]
          => /o/
    END
    """)[0]
    w = wf.make_word("ko'raj.ka")
    nw = sc.apply(w)
    assert repr(nw) == "/ko.'rej.ko/"


def test_multiple_conditional_with_relexp(wf):
    sc = parser.compile("""
    CHANGE BEGIN
      {/a/, /aː/} => {/e/, /eː/} | _[+front]
                  => {/ə/, /oː/}
    END
    """)[0]

    word1 = wf.make_word("ka.laj'kaː")
    word2 = wf.make_word("paː'jet.na")
    nw1 = sc.apply(word1)
    nw2 = sc.apply(word2)

    assert repr(nw1) == "/kə.lej.'koː/"
    assert repr(nw2) == "/peː.'jet.nə/"


def test_change_feature_conditional_with_relexp(wf):
    sc = parser.compile("""
    CHANGE BEGIN
      [+sibilant] => [+voice]    | [-consonantal]_[-consonantal]
                  => [+front]    | _[-consonantal +front]
                  => [+sibilant]
    END
    """)[0]

    w1 = wf.make_word("mak'si.ra")
    w2 = wf.make_word("ma'sa.la")
    w3 = wf.make_word("pe'si.ka")
    w4 = wf.make_word("sa'mo.ŋe")

    nws = [repr(sc.apply(w)) for w in [w1, w2, w3, w4]]
    assert nws == ["/mak.'ɕi.ra/", "/ma.'za.la/", "/pe.'ʑi.ka/", "/sa.'mo.ŋe/"]


def test_replace_by_feature_conditional_with_relexp(wf):
    sc = parser.compile("""
    CHANGE BEGIN
      [+sibilant] => /0/ | [-consonantal]_[-consonantal]
                  => /h/
    END
    """)[0]

    words = [wf.make_word(w) for w in ["sa.lo.ka", "ke.se.nam", "pas.ko.ne",
                                       "lak.si.nam", "a.tas"]]
    new_words = [repr(sc.apply(w)) for w in words]
    assert new_words == ["/ha.lo.ka/", "/ke.e.nam/", "/pah.ko.ne/",
                         "/lak.hi.nam/", "/a.tah/"]


def test_word_break_initial_in_relexp(wf):
    sc = parser.compile("CHANGE BEGIN /o/ -> /we/ | #_ END")[0]
    words = [wf.make_word(w) for w in ["ok.to", "a.po.lo", "te.o.lo", "kon.dre.lo"]]
    new_words = [repr(sc.apply(w)) for w in words]
    assert new_words == ["/wek.to/", "/a.po.lo/", "/te.o.lo/",
                         "/kon.dre.lo/"]


def test_word_break_final_in_relexp(wf):
    sc = parser.compile("CHANGE BEGIN /o/ -> /u/ | _# END")[0]
    words = [wf.make_word(w) for w in ["ok.to", "a.po.lo", "te.o.lo", "kon.dre.lo"]]
    new_words = [repr(sc.apply(w)) for w in words]
    assert new_words == ["/ok.tu/", "/a.po.lu/", "/te.o.lu/",
                         "/kon.dre.lu/"]


def test_compound_expression_with_word_break_in_relexp(wf):
    sc = parser.compile("CHANGE BEGIN /o/ -> /we/ | #[+consonantal]_ END")[0]
    words = [wf.make_word(w) for w in ["ok.to", "a.po.lo", "te.o.lo", "kon.dre.lo"]]
    new_words = [repr(sc.apply(w)) for w in words]
    assert new_words == ["/ok.to/", "/a.po.lo/", "/te.o.lo/",
                         "/kwen.dre.lo/"]
