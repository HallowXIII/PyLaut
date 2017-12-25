import typing
from typing import List
from pylaut.change import *
from pylaut.word import Word, WordFactory, Syllable
from pylaut.phone import Phone

def change_feature(phone: Phone, name: str, value: bool) -> Phone:
    np = deepcopy(phone)
    if value:
        np.set_features_true(name)
    else:
        np.set_features_false(name)
    np.set_symbol_from_features()
    return np

def delete_phonemes(syllable: Syllable, phonemes: List[Phoneme]) -> Syllable:
    syllable.phonemes = [p for p in syllable.phonemes if p not in phonemes]
    return syllable

def before_stress(td: Transducer) -> bool:
    wstr = td.word.get_stressed_position()
    if wstr is None:
        return False
    else:
        return (td.syllables.index(td.syllable) < wstr)

def after_stress(td: Transducer) -> bool:
    wstr = td.word.get_stressed_position()
    if wstr is None:
        return False
    else:
        return (td.syllables.index(td.syllable) > wstr)
