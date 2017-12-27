from pylaut import lexicon
from pylaut.change import *
from pylaut.change_functions import *

def make_latin_lexicon():
    with open("vulgarlatin.lex","r") as raw_lexicon:
        read_words = [x for x in raw_lexicon.read().splitlines() if x[0] != "#"]
        split_words = [x.split() for x in read_words]

    latin_lexicon = lexicon.Lexicon()

    latin_lexicon.language = "Vulgar Latin"
    latin_lexicon.set_date(200,"AD")

    #make Lexicons
    for line in split_words:
        latin_lexicon.add_entry(lexicon.LexiconEntry(*line))

    latin_lexicon.init_phonology()

    latin_phonology = latin_lexicon.phonology

    syllable_types = set()

    onsets, nuclei, codas = [], [], []

    for entry in latin_lexicon.entries:
        for syllable in entry.phonetic.syllables:
            struct = syllable.get_structure()
            onsets += [struct[0]]
            nuclei += [struct[1]]
            codas += [struct[2]]

    latin_phonology.set_phoneme_frequency_from_list("onset",onsets)
    latin_phonology.set_phoneme_frequency_from_list("nucleus",nuclei)
    latin_phonology.set_phoneme_frequency_from_list("coda",codas)

    return latin_lexicon

timber_collapse = unconditional(map(Phoneme, ["ɪ", "ʊ"]), map(Phoneme, ["e", "o"]))
coalesce_e = Change().do(lambda s: Syllable(
    s.get_onset() + [Phoneme("e")] + s.get_coda())).to(This.forall(Syllable)(
        lambda s: is_diphthong(s.get_nucleus(), "oi")
        or is_diphthong(s.get_nucleus(), "ai")))

coalesce_o = Change().do(lambda s: Syllable(
    s.get_onset() + [Phoneme("o")] + s.get_coda())).to(This.forall(Syllable)(
        lambda s: is_diphthong(s.get_nucleus(), "au")))

def main():

    latin_lexicon = make_latin_lexicon()
    latin_phonology = latin_lexicon.phonology

    for entry in latin_lexicon.entries:
        entry.phonetic = timber_collapse.apply(entry.phonetic)
        print(entry)

if __name__ == "__main__":
    main()
