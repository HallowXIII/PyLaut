from pylaut.change.change import Change, This, Transducer
from pylaut.phone import Phone
from pylaut.phonology import Phonology, Phoneme
from pylaut.language.phonology.word import Word, WordFactory, Syllable
from pylaut.change_functions import (before_stress, delete_phonemes,
                                     change_feature)


def main():

    phonemes = [
        "p", "t", "k", "b", "d", "ɡ", "m", "n", "s", "f", "x", "w", "j", "r",
        "l", "a", "e", "i", "o", "u"
    ]
    phonology = Phonology(phonemes)

    wf = WordFactory(phonology)

    raw_words = ["ta'sap", "i.be'ko.mu", "uk.tu'ku"]
    words = [wf.make_word(rw) for rw in raw_words]

    # b -> v / _$[+stressed]
    ch = Change().do(lambda x: Phoneme("v")).to(
        This.forall(Phone)(lambda p: p.is_symbol("b"))).when(
            This.at(Syllable, 1, lambda a: a.is_stressed()))

    # C[-continuant -voice] -> C[-continuant +voice] / V_V
    c2 = Change(
    ).do(lambda this: change_feature(this.phoneme, "voice", True)).to(
        This.forall(Phone)(lambda p: p.feature_is_false("continuant"))).when(
            This.at(Phone, -1, lambda p: p.is_vowel())).when(
                This.at(Phone, 1, lambda p: p.is_vowel()))

    c3 = Change().do(
        lambda this: delete_phonemes(this.syllable, this.syllable.get_onset())
    ).to(This.forall(Syllable)(lambda s: s.is_initial())).unless(
        This.at(Syllable, 0, lambda s: s.is_stressed()))

    c4 = Change().do(lambda p: Phoneme("ə")).to(
        This.forall(Phone)
        (lambda p: p.is_symbol("u") or p.is_symbol("i"))).when(before_stress)

    changed = list(
        map(c4.apply, map(c3.apply, map(c2.apply, map(ch.apply, words)))))
    print(changed)


if __name__ == '__main__':

    main()
