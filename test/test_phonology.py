"""
Test module for phonology.py
"""

import pytest
from pylaut.language.phonology import phonology


@pytest.fixture
def vowels():
    return {"aː", "iː", "uː", "a", "i", "u", "ə"}


@pytest.fixture
def consonants():
    return {"p", "t", "k", "s", "x", "r", "l", "w"}


@pytest.fixture
def sample_phonology(vowels, consonants):
    return phonology.Phonology(vowels | consonants)


@pytest.fixture
def sample_phonology_with_subsystems(sample_phonology):
    sample_phonology.define_vowel_subsystem('long', autoadd=True)
    return sample_phonology


@pytest.fixture
def long_vowels():
    return {"aː", "iː", "uː"}


@pytest.fixture
def phoneme():
    return phonology.Phoneme("a")


def test_vowel_subsystems_keys(sample_phonology):
    sample_phonology.define_vowel_subsystem("long", autoadd=True)
    assert '+long' in sample_phonology.vowel_subsystems
    assert '-long' in sample_phonology.vowel_subsystems


def test_vowel_subsystems_contents(sample_phonology, long_vowels):
    sample_phonology.define_vowel_subsystem("long", autoadd=True)
    assert {ph.symbol
            for ph in sample_phonology.vowel_subsystems['+long']
            } == long_vowels


def test_json(sample_phonology):
    json = sample_phonology.to_json()
    new_phonology = phonology.Phonology()
    new_phonology.from_json(json)
    assert ({ph.symbol
             for ph in new_phonology.phonemes} == {
                 ph.symbol
                 for ph in sample_phonology.phonemes
             })


def test_add_phoneme(sample_phonology, phoneme):
    sample_phonology.add_phoneme(phoneme)
    assert phoneme in sample_phonology.phonemes


def test_add_phoneme_errors(sample_phonology):
    with pytest.raises(TypeError):
        sample_phonology.add_phoneme("a")


def test_get_vowels(sample_phonology):
    vwls = {ph.symbol for ph in sample_phonology.get_vowels()}
    assert vwls == {"aː", "iː", "uː", "a", "i", "u", "ə"}


def test_get_consonants(sample_phonology):
    vwls = {ph.symbol for ph in sample_phonology.get_consonants()}
    assert vwls == {"p", "t", "k", "s", "x", "r", "l", "w"}


def test_get_phoneme(sample_phonology):
    ph = sample_phonology.get_phoneme("a")
    assert ph


def test_get_phoneme_errors(sample_phonology):
    with pytest.raises(Exception):
        sample_phonology.get_phoneme("y")


def test_get_phonemes_with_feature(sample_phonology, consonants):
    cps = sample_phonology.get_phonemes_with_feature('consonantal', '+')
    cs = {ph.symbol for ph in cps}
    assert cs == consonants


def test_get_phonemes_with_features(sample_phonology, long_vowels):
    lvp = sample_phonology.get_phonemes_with_features({
        'consonantal': '-',
        'long': '+'
    })
    lv = {ph.symbol for ph in lvp}
    assert lv == long_vowels


def test_get_phoneme_dictionary_keys(sample_phonology, vowels, consonants):
    pdict = sample_phonology.get_phoneme_dictionary()
    assert set(pdict.keys()) == vowels | consonants


def test_get_phoneme_dictionary_types(sample_phonology, vowels, consonants):
    pdict = sample_phonology.get_phoneme_dictionary()
    assert all(isinstance(k, str) for k in pdict.keys())
    assert all(isinstance(v, phonology.Phoneme) for v in pdict.values())


def test_set_phoneme_frequency_from_list_errors(sample_phonology):
    with pytest.raises(Exception):
        sample_phonology.set_phoneme_frequency_from_list('nuculus', [])


def test_set_phoneme_frequency_from_list(sample_phonology, vowels):
    plist = [phonology.Phoneme(p) for p in vowels]
    sample_phonology.set_phoneme_frequency_from_list('nucleus', plist)
    pf = sample_phonology.nucleus_frequencies
    for phon, freq in pf.items():
        assert freq == 1 / len(vowels)


def test_get_total_phoneme_frequency(sample_phonology, vowels):
    plist = [phonology.Phoneme(p) for p in vowels]
    sample_phonology.set_phoneme_frequency_from_list('onset', plist)
    sample_phonology.set_phoneme_frequency_from_list('nucleus', plist)
    sample_phonology.set_phoneme_frequency_from_list('coda', plist)
    tf = sample_phonology.get_phoneme_frequency_total(
        sample_phonology.get_phoneme('a'))
    assert tf == 1 / len(vowels)


def test_get_total_phoneme_frequency_error(sample_phonology):
    with pytest.raises(TypeError):
        sample_phonology.get_phoneme_frequency_total("a")


def test_assign_vowel_to_subsystem_not_phoneme(
        sample_phonology_with_subsystems):
    with pytest.raises(Exception):
        sample_phonology_with_subsystems.assign_vowel_to_subsystem(
            'a', 'long', '+')


def test_assign_vowel_to_subsystem_not_vowel(sample_phonology_with_subsystems):
    with pytest.raises(Exception):
        sample_phonology_with_subsystems.assign_vowel_to_subsystem(
            sample_phonology_with_subsystems.get_phoneme('p'), 'long', '+')


def test_assign_vowel_to_subsystem_invalid_subsystem(
        sample_phonology_with_subsystems):
    with pytest.raises(Exception):
        sample_phonology_with_subsystems.assign_vowel_to_subsystem(
            sample_phonology_with_subsystems.get_phoneme('a'), 'fruity', '+')


def test_assign_vowel_to_subsystem(sample_phonology_with_subsystems):
    sample_phonology_with_subsystems.assign_vowel_to_subsystem(
        sample_phonology_with_subsystems.get_phoneme('a'), 'long', '-')


def test_get_vowels_in_subsystem(sample_phonology_with_subsystems):
    longs = sample_phonology_with_subsystems.get_vowels_in_subsystem(
        'long', '+')
    assert isinstance(longs, set)


def test_get_vowel_subsystems(sample_phonology_with_subsystems):
    subs = sample_phonology_with_subsystems.get_vowel_subsystems()
    assert subs == ['long']


def test_count_vowels(sample_phonology_with_subsystems):
    cmp_dict = {'total': 7, 'long': {'+': 3, '-': 4}}
    count_dict = sample_phonology_with_subsystems.count_vowels()
    assert count_dict == cmp_dict
