#http://stackoverflow.com/posts/11158224/revisions
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

import lexicon

if __name__ == "__main__":

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

for word in latin_lexicon.entries:
    print(word.lexicon_entry())

latin_phonology = latin_lexicon.phonology
print(latin_phonology.get_vowels())
print(latin_phonology.get_consonants())

syllable_types = set()

onsets, nuclei, codas = [], [], []

for entry in latin_lexicon.entries:
    for syllable in entry.phonetic.syllables:
        struct = syllable.get_structure()
        onsets += [struct[0]]
        nuclei += [struct[1]]
        codas += [struct[2]]
#        vs = []
#        vs = "".join(["V" if x.is_vowel() else "C" for x in syllable.phonemes])
#        syllable_types.add(vs)
#        print(list(zip(syllable.phonemes,vs)))
#        print(syllable.get_structure())
#        if syllable.has_clusters():
#            print(syllable.get_clusters())

latin_phonology.set_phoneme_frequency_from_list("onset",onsets)
latin_phonology.set_phoneme_frequency_from_list("nucleus",nuclei)
latin_phonology.set_phoneme_frequency_from_list("coda",codas)
