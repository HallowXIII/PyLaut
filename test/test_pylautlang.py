from pkgutil import get_data
from pylaut.phone import Phone
from pylaut.phonology import Phonology, Phoneme
from pylaut.word import Word, WordFactory, Syllable
from pylaut.parser import get_parser, PyLautLang
from pylaut.pylautlanglib import get_library
from pylaut.change_functions import Resyllabify

import shaptoem

def get_scfile():
    with open("martial.sc") as scfile:
        sc = scfile.read()
    return sc


def get_lexicon():
    with open("shap.lex") as lexfile:
        lexicon = lexfile.readlines()
        lexicon = [s.strip() for s in lexicon]
    return lexicon


def get_word_factory():
    phonemes = ["p", "t", "k",
                "b", "d", "ɡ",
                "m", "n", "ŋ",
                "f", "θ", "h", "s", "z", "ʃ",
                "r", "l",
                "i", "e", "o", "u", "ɯ", "ə", "a", "ɒ",
                "iː", "eː", "oː", "uː", "ɯː", "əː", "aː", "ɒː"]
    phonology = Phonology(phonemes)

    return WordFactory(phonology)

def main():
    f = get_scfile()
    l = get_lexicon()

    wf = get_word_factory()
    library = get_library()
    library["Resyllabify"] = lambda *_: Resyllabify(wf=wf)
    pl = PyLautLang(library)
    tt = pl.compile(f)

    manual_changes = shaptoem.get_changes()

    l1 = [wf.make_word(w) for w in l]
    l2 = [wf.make_word(w) for w in l]
    for w1, w2 in zip(l1, l2):
        nw1 = w1
        nw2 = w2
        for change in tt:
            nw1 = change(nw1)
        print("Auto: {} -> {}".format(w1, nw1))
        # for change in manual_changes:
        #     nw2 = change(nw2)
        # print("Manual: {} -> {}".format(w2, nw2))


if __name__ == "__main__":
    main()
