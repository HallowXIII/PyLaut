from pylaut.language import phonology
import pytest

def test_syllable_nuclei():
    wf = phonology.word.WordFactory()
    w = wf.make_word('pæev')
    s = w.syllables[0]
    n_nuclei = s.count_nuclei()
    assert n_nuclei == 1


def test_syllabification():
    wf = phonology.word.WordFactory()
    w = wf.fromlist('pæevaks')
    assert len(w.syllables) == 2
