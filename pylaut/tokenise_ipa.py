from itertools import tee
from pkgutil import get_data
from pylaut import utils

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def tokenise_ipa(s, feature_set=None):
    """
    Outputs a tuple of tokenised ipa symbols, with diacritics grouped with base
    glyphs. If the ipa is presented sI'lab.ik.lI, it outputs a tuple of tuples
    """
    if not feature_set:
        dia_file = get_data("pylaut", "data/monophone_ipa_diacritics").decode(
            'utf-8')
        read_words = [x for x in dia_file.splitlines()]
        diacritics = [x.split()[0] for x in read_words]
    else:
        diacritics = feature_set._feature_set_ipa_diacritics.keys()

    s = utils.replace(s, "'", ".'")
    sl = utils.split(s, ".")

    tokens = []

    for syllable in sl:
        syllable_tokens = []
        # if syllable and syllable[0] == "'":
        #     stress = "'"
        #     syl = syllable[1:]
        # else:
        #     stress = ""
        #     syl = syllable
        syl = syllable

        for i, c in enumerate(syl):
            if c in diacritics:
                pass
            elif i < len(syl)-1 and syl[i+1] in diacritics:
                syllable_tokens += [c + syl[i+1]]
            else:
                syllable_tokens += [c]

        tokens += [syllable_tokens]

        out = [tuple(x) for x in tokens]

        if len(out) == 1:
            out = out[0]

        out = tuple(t for t in out if t is not ())

    return out


def syllabify(seglist: list, sep: str) -> list:
    pass
