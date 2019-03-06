import copy
from itertools import zip_longest
from typing import Iterable, List, Optional

import pylaut.change.change as change
from pylaut.language.phonology.phone import Phone
from pylaut.language.phonology.phonology import Phoneme, Phonology
from pylaut.language.phonology.word import Syllable, Word, WordFactory


class Contour(Phoneme):
    def __init__(self, plist):
        super().__init__()
        self.children = plist
        self.symbol = "".join(p.symbol for p in self.children)

    def __repr__(self):
        return "".join(["/", self.symbol, "/"])


class ComplexDomain(change.Change):
    def __init__(self, plist):
        super().__init__()
        self.contour = plist

    def apply(self, word_obj):
        return super().apply(sequence_to_contour(word_obj, self.contour))


class Resyllabify(change.Change):
    def __init__(self, wf=None):
        super().__init__()
        self.wf = wf

    def apply(self, word_obj):
        segs = [p.symbol for p in word_obj.phonemes]
        if not self.wf:
            self.wf = WordFactory(Phonology(segs))
        return self.wf.fromlist(segs)


def match_subsequence(w: Word, ph: Phoneme,
                      seq: List[Phoneme]) -> Optional[List[Phoneme]]:
    symbols = list(map(lambda p: p.symbol, seq))
    idx = w.phonemes.index(ph)
    match = False
    if ph.symbol in symbols:
        try:
            subsymbols = symbols[symbols.index(ph.symbol):]
            subsequence = w.phonemes[idx:idx + len(subsymbols)]
            match = all(
                p.is_symbol(q.symbol) for (p, q) in zip(seq, subsequence))
        except IndexError:
            pass
    return subsequence if match else None


def delete_phonemes_from_word(w: Word, seq: List[Phoneme]):
    for s in w.syllables:
        s.phonemes = [p for p in s.phonemes if p not in seq]
    w.phonemes = [p for s in w.syllables for p in s.phonemes]


def sequence_to_contour(w: Word, seq: List[Phoneme]) -> Word:
    if len(seq) == 1:
        return w
    for syllable in w.syllables:
        for i in range(len(syllable.phonemes)):
            try:
                subseq = match_subsequence(w, syllable.phonemes[i], seq)
            except IndexError:
                break
            if subseq is not None:
                syllable.phonemes[i] = Contour(subseq)
                delete_phonemes_from_word(w, subseq)
    return w


def change_feature(phone: Phone, name: str, value: str) -> Phone:
    np = copy.deepcopy(phone)
    if value == '+':
        np.set_features_true(name)
    elif value == '-':
        np.set_features_false(name)
    np.set_symbol_from_features()
    return np


def delete_phonemes(syllable: Syllable,
                    phonemes: Iterable[Phoneme]) -> Syllable:
    syllable.phonemes = [p for p in syllable.phonemes if p not in phonemes]
    return syllable


def before_stress(td: change.Transducer) -> bool:
    wstr = td.word.get_stressed_position()
    if wstr is None:
        return False
    else:
        return (td.syllables.index(td.syllable) < wstr)


def after_stress(td: change.Transducer) -> bool:
    wstr = td.word.get_stressed_position()
    if wstr is None:
        return False
    else:
        return (td.syllables.index(td.syllable) > wstr)


def replace_phonemes(domain: List[Phone],
                     codomain: List[Phone]) -> change.Change:

    dom = Contour(domain)
    return ComplexDomain(domain).do(lambda x: codomain).to(
        change.This.forall(Phone)(lambda p: p.is_symbol(dom.symbol)))


def is_diphthong(nucleus: Iterable[Phone], diphthong: Iterable[str]) -> bool:
    for ch, v in zip_longest(diphthong, nucleus):
        try:
            if not v.is_symbol(ch):
                return False
        except AttributeError:
            return False
    return True
