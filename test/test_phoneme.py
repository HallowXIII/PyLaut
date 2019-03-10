"""
Test of the Phoneme class.
We're relying on a hell of a lot of monophone-specific
feature check methods especially in pylautlang so first
we need to check for that.
"""

import pytest
from pylaut.language.phonology.phonology import Phoneme


@pytest.fixture
def phone():
    return Phoneme('e')


def test_get_sonority(phone):
    phone.get_sonority()


def test_is_approximant(phone):
    phone.is_approximant()


def test_is_back_vowel(phone):
    phone.is_back_vowel()


def test_is_central_vowel(phone):
    phone.is_central_vowel()


def test_is_consonant(phone):
    phone.is_consonant()


def test_is_fricative(phone):
    phone.is_fricative()


def test_is_front_vowel(phone):
    phone.is_front_vowel()


def test_is_high_vowel(phone):
    phone.is_high_vowel()


def test_is_lateral_approximant(phone):
    phone.is_lateral_approximant()


def test_is_low_vowel(phone):
    phone.is_low_vowel()


def test_is_mid_vowel(phone):
    phone.is_mid_vowel()


def test_is_nasal_stop(phone):
    phone.is_nasal_stop()


def test_is_rounded_vowel(phone):
    phone.is_rounded_vowel()


def test_is_stop(phone):
    phone.is_stop()


def test_is_tone(phone):
    phone.is_tone()


def test_is_voiced_consonant(phone):
    phone.is_voiced_consonant()


def test_is_vowel(phone):
    phone.is_vowel()
