from pylaut.word import WordFactory, Syllable
from pylaut.phone import Phone
from pylaut.phonology import Phoneme, Phonology
from pylaut.change import *
from pylaut.change_functions import change_feature

def metathesize(syl, index, offset):
    ns = syl.copy()
    ns.phonemes[index], ns.phonemes[index+offset] = (
        ns.phonemes[index+offset], ns.phonemes[index]
    )
    return ns

def is_sibilant(seg):
    return (seg.feature_is_true("consonantal")
            and seg.feature_is_true("continuant")
            and seg.feature_is_true("coronal")
            and seg.feature_is_false("dental"))

def is_voiceless_sibilant(seg):
    return is_sibilant(seg) and not seg.is_voiced_consonant()

def main():
    
    zsr = Change().do(lambda x: Phoneme("m")).to(This.forall(Phone)(
        lambda p: p.is_symbol("p"))).when(
            This.at(Phone, 1, lambda p: is_sibilant(p)))

    mt = Change().do(lambda s: metathesize(
        s, s.phonemes.index(s.get_nucleus()[0]), -1)).to(
            This.forall(Syllable)(lambda s: s.get_nucleus()[0].is_vowel()
                and is_voiceless_sibilant(s.phonemes[s.phonemes.index(
                    s.get_nucleus()[0])-1])))

    vlength = Change().do(lambda p: change_feature(p, "long", True)).to(
        This.forall(Phone)(lambda p: p.is_vowel())).when(
            This.at(Phone, 1, lambda p: is_voiceless_sibilant(p)))

    shtosn = Change().do(lambda p: [Phoneme("s"), Phoneme("n")]).to(
        This.forall(Phone)(lambda p: p.is_symbol("ʃ")))

    devoice_z = Change().do(lambda p: change_feature(p, "voice", False)).to(
        This.forall(Phone)(lambda p: p.is_symbol("z")))

    h_lengthen1 = Change().do(lambda p: change_feature(p, "long", True)).to(
        This.forall(Phone)(lambda p: p.is_vowel())).when(
            This.at(Phone, -1, lambda c: c.is_symbol("h")))

    h_lengthen2 = Change().do(lambda p: change_feature(p, "long", True)).to(
        This.forall(Phone)(lambda p: p.is_vowel())).when(
            This.at(Phone, 1, lambda c: c.is_symbol("h")))

    htoa1 = Change().do(lambda p: Phoneme("aː")).to(This.forall(Phone)(
        lambda p: p.is_symbol("h"))).when(This.at(Phone, -1,
            lambda c: c.is_consonant())).when(
                This.at(Phone, 1, lambda c: c.is_consonant()))

    htoa2 = Change().do(lambda p: Phoneme("aː")).to(This.forall(Phone)(
        lambda p: p.is_symbol("h"))).when(This.at(Phone, -1,
            lambda c: c.is_consonant())).when(
                This.is_at_index(Phone, -1))

    delete_h = Change().do(lambda p: []).to(This.forall(Phone)(
        lambda p: p.is_symbol("h")))

    voice_f = Change().do(lambda p: Phoneme("v")).to(This.forall(Phone)(
        lambda p: p.is_symbol("f"))).when(This.at(Phone, -1,
            lambda v: v.is_vowel())).when(
                This.at(Phone, 1, lambda v: v.is_vowel()))

    thtoz = Change().do(lambda p: Phoneme("z")).to(This.forall(Phone)(
        lambda p: p.is_symbol("θ")))

    changes = [zsr, mt, vlength, shtosn, devoice_z, h_lengthen1,
               h_lengthen2, htoa1, htoa2, delete_h, voice_f, thtoz]

    shap_phon = Phonology([
        "p","t","k",
        "b","d","ɡ",
        "f","θ","h",
        "s","z","ʃ",
        "r",
        "i","u","ɯ","ə","a","ɒ"])
    wf = WordFactory(shap_phon)
    with open("shap.lex") as sl:
        raw = sl.readlines()
        words = [wf.make_word(w.strip()) for w in raw]
        new_words = [w.copy() for w in words]
        for change in changes:
            new_words = [change.apply(w) for w in new_words]

    print(words)
    print(new_words)
                
if __name__ == '__main__':
    main()
