import shaptoem
from pylaut.change.change_functions import Resyllabify
from pylaut.language.phonology.phonology import Phonology
from pylaut.language.phonology.word import WordFactory
from pylaut.pylautlang.lib import get_library
from pylaut.pylautlang.parser import PyLautLang, get_parser


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

def transform_martial():
    f = get_scfile()
    p = get_parser()
    t = p.parse(f)
    # wf = get_word_factory()
    library = get_library()
    # library["Resyllabify"] = lambda *_: Resyllabify(wf=wf)
    pl = PyLautLang(library)
    # t = pl.parser.parse(f)
    # print(t.pretty())
    tt = pl.transform(t)
    return t, tt

def main():
    l = get_lexicon()
    t, tt = transform_martial()
    print(t.pretty())
    print(tt)

    # manual_changes = shaptoem.get_changes()
    wf = WordFactory()
    l1 = [wf.make_word(w) for w in l]
    # l2 = [wf.make_word(w) for w in l]
    for w in l1:
        nw = w
        for change in tt:
            nw = change.apply(nw)
        print("Auto: {} -> {}".format(w, nw))
    # for w1, w2 in zip(l1, l2):
    #     nw1 = w1
    #     nw2 = w2
    #     for change in tt:
    #         nw1 = change(nw1)
    #     print("Auto: {} -> {}".format(w1, nw1))
        # for change in manual_changes:
        #     nw2 = change(nw2)
        # print("Manual: {} -> {}".format(w2, nw2))


if __name__ == "__main__":
    main()
