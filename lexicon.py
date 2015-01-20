import word, phonology

class Lexicon(object):

    def __init__(self):
        self.language = None
        self.date = None
        
        self.phonology = None
        self.word_factory = None
        
        self.entries = list()

    def set_date(self,value,system):
        self.date = (value,system)
        
    def add_entry(self,lexicon_entry):
        self.entries += [lexicon_entry]
        
    def init_phonology(self):
        #extract phonemes
        phonemes = set()
        for entry in self.entries:
            #TODO: a call to a real IPA tokeniser
            for symbol in entry.ipa:
                if symbol not in "'.":
                    phonemes.add(symbol)

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

