import word, phonology
from tokenise_ipa import tokenise_ipa
import random

class Lexicon(object):

    def __init__(self):
        self.language = None
        self.date = None
        
        self.phonology = None
        self.word_factory = None
        
        self.entries = list()

    def get_random_entry(self):
        return random.choice(self.entries)
    
    def get_random_entry_with_segment(self,segment):
        rand_entry = ""
        while segment not in rand_entry.__repr__():
            rand_entry = self.get_random_entry()
        return rand_entry
        
    def from_file(self,file_obj):
        with file_obj as raw_lexicon:
            read_words = [x for x in raw_lexicon.read().splitlines() if x[0] != "#"]
            split_words = [x.split() for x in read_words]
        
        #make Lexicons
        for line in split_words:
            self.add_entry(LexiconEntry(*line))

        self.init_phonology()
        
    def set_date(self,value,system):
        self.date = (value,system)
        
    def add_entry(self,lexicon_entry):
        self.entries += [lexicon_entry]
        
    def init_phonology(self):
        #extract phonemes
        phonemes = set()
        for entry in self.entries:
            tokenised = tokenise_ipa(entry.ipa)
            for syllable in tokenised:
                for phoneme in syllable:
                    phonemes.add(phoneme)

        self.phonology = phonology.Phonology(list(phonemes))
        self.factory = word.WordFactory(self.phonology)
        
        for entry in self.entries:
            entry.set_phonetic(self.factory.make_word(entry.ipa))

class LexiconEntry(object):

    def __init__(self,ipa_string,ortho_string,gloss):
        self.ipa = ipa_string
        self.orthography = ortho_string
        self.gloss = gloss
        self.phonetic = None
    
    def lexicon_entry(self):
        return "{} {}: {}".format(self.orthography,self.__repr__(),self.gloss)
                 
    def __repr__(self):
        if self.phonetic:
            return str(self.phonetic)
        else:
            return "*/"+self.ipa+"/"
    
    def set_phonetic(self,phonetic_word):
        self.phonetic = phonetic_word

