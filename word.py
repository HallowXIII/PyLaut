from phone import MonoPhone
from phonology import Phonology

class Syllable(object):
    def __init__(self,phonemes):
        self.phonemes = phonemes
        self.stressed = False
        self.word_position = None

    def __repr__(self):
        output = [] if self.word_position in ["initial","monosyllable"] else ["-"]
        
        if self.stressed:
            output += ["'"]
        
        for phoneme in self.phonemes:
            output += [phoneme.symbol]
        
        if self.word_position not in ["final","monosyllable"]:
            output += ["-"]
            
        return "".join(output)
    
    def is_stressed(self):
        self.stressed = True
        
    def is_unstressed(self):
        self.stressed = False
        
    def set_word_position(self,position):
        if position not in ["initial","medial","final","monosyllable"]:
            raise Exception()
        else:
            self.word_position = position
    
    def get_word_position(self):
        return self.word_position
    
    def is_initial(self):
        if self.get_word_position() == "initial":
            return True
        else:
            return False
            
    def is_medial(self):
        if self.get_word_position() == "medial":
            return True
        else:
            return False

    def is_final(self):
        if self.get_word_position() == "final":
            return True
        else:
            return False
            
    def is_monosyllable(self):
        if self.get_word_position() == "monosyllable":
            return True
        else:
            return False
    #TODO
    
    def count_nuclei(self):
        """
        Returns an estimated number of nuclei in this syllable.
        If the value is greater than 1, something is likely wrong, e.g. the source
        has been incorrectly syllabified. If it is less than 1 either something 
        is wrong, or you are in the PNW.
        """
        pass
        #check to see if there are phones w/ sonorities >= 10        
        #reduce all vowels to level 10, n := 10

        #if there are none, check for sonorities >= 5 and use max as n

        #if there are neither, return 0
        
        #group together all adjacent ns
        
        #return the number of ns in the list
 
    def get_onset(self):
        pass
    def get_nucleus(self):
        pass
    def get_coda(self):
        pass
    
    def get_rime(self):
        return self.get_nucleus() + self.get_coda()
        
    def is_open(self):
        if not self.get_coda():
            return True
        else:
            return False
            
    def is_closed(self):
        return not self.is_open()
             
    def get_clusters(self):
        """
        Return a list of tuples of consonant clusters present in this syllable
        """
        pass
    
    def get_polyphthongs(self,glides=False):    
        """
        Return a list of tuples of polypthongs present in this syllable
        If 'glides' is True, then semivowels count as vowels
        """
        pass
        
class Word(object):
    def __init__(self,syllables):
        self.syllables = syllables

    def __repr__(self):
        word_repr = "/"
        for syl in self.syllables:
            if syl.word_position == "initial":
                word_repr += syl.__repr__()[:-1] + "."
            elif syl.word_position == "medial":
                word_repr += syl.__repr__()[1:-1] + "."
            elif syl.word_position == "final":
                word_repr += syl.__repr__()[1:] + "/"
            else:
                word_repr += syl.__repr__() + "/"
        
        return word_repr


        
class WordFactory(object):
    """
    Makes Words.
    Needs to be initialised with a Phonology.
    make_words takes an IPA string, syllables delimited with <.> or <'> if stressed 
    and outputs a Word, composed of Syllables.
    """
    def __init__(self,phonology):
        self.phonology = phonology
        self.phoneme_dict = self.phonology.get_phoneme_dictionary()
        
        
    def make_word(self,raw_word):
        #turn ' into .' to allow splitting into syllables
        raw_word = raw_word.replace("'",".'")
        raw_syllables = [syl for syl in raw_word.split(".") if syl]
        syllables = []
        for i, rs in enumerate(raw_syllables):
            syl = []
            stressed = False
            
            #if there is a "'", this syllable has stress
            if rs[0] == "'":
                stressed = True
            
            if i == 0:
                word_position = "initial"
            elif i == len(raw_syllables)-1:
                word_position = "final"
            else:
                word_position = "medial"
            
            if len(raw_syllables) == 1:
                word_position = "monosyllable"
                
            #TODO identify diacritics
            proto_syl = []
            
            if stressed:
                proto_rs = rs[1:]
            else:
                proto_rs = rs
            
            for ipa_char in proto_rs:
                proto_syl += [self.phoneme_dict[ipa_char]]
            syl = Syllable(proto_syl)
            if stressed:
                syl.is_stressed()
            
            syl.set_word_position(word_position)
            syllables += [syl]
        
        
        word = Word(syllables)
        return word

################################################################################

if __name__ == '__main__':

    #example phonology
    phonemes = ["p","t","k",
                "b","d","g",
                "m","n",
                "s","f",
                "w","j",
                "r","l",
                "a","e","i","o","u"]
    phonology = Phonology(phonemes)

    wf = WordFactory(phonology)
    
    raw_words = ["a'ma.re","'ka.sa","'ar.bo.re","et","ak'tjo.ne"]
    words = []
    for word in raw_words:
        words += [wf.make_word(word)]
    print(words)
