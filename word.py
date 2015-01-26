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
    
    def contains_vowel(self):
        types = [ph.is_vowel() for ph in self.phonemes]
        if True in types:
            return True
        else:
            return False
            
    def count_nuclei(self):
        """
        Returns an estimated number of nuclei in this syllable.
        If the value is greater than 1, something is likely wrong, e.g. the source
        has been incorrectly syllabified. If it is less than 1 either something 
        is wrong, or you are in the PNW.
        """
        sonorities = [ph.get_sonority() for ph in self.phonemes]
        #check to see if there are phones w/ sonorities >= 10        
        if max(sonorities) >= 10:
            maximum_sonority = 10
        #reduce all vowels to level 10, n := 10
            sonorities = [10 if s > 10 else s for s in sonorities]
        #if there are none, check for sonorities >= 5 and use max as n
        elif max(sonorities) >= 5:
            maximum_sonority = max(sonorities)
        #if there are neither, return 0
        else:
            return 0
        
        #group together all adjacent ns
        #TODO: fun fact: len(a) is too big, and a smaller value will work. find it
        for m in range(len(sonorities)):
            for i, n in enumerate(sonorities):
                if i > 0 and sonorities[i-1] == n:
                    sonorities[i] = None
            sonorities = [x for x in sonorities if x]

        #return the number of ns in the list
        return len([x for x in sonorities if x == maximum_sonority])
    
    def get_structure(self):
        nuclei_num = self.count_nuclei()
        if nuclei_num < 1:
            raise Exception("Syllable {} has no nucleus!".format(self))
        elif nuclei_num > 1:
            raise Exception("Syllable {} has {} nuclei!".format(self,nuclei_num))
        else:
            pass
        
        sonorities = [ph.get_sonority() for ph in self.phonemes]
        
        onset, nucleus, coda = [], [], []
        if self.contains_vowel(): #the job is easier!
            n,c = False,False
            for i, ph in enumerate(self.phonemes):
                #we haven't triggered either nucleus or coda bit + is C
                if not n and not c and ph.is_consonant():
                    onset += [ph]
                #we haven't triggered either nucleus or coda bit + is V
                elif not n and not c and ph.is_vowel():
                    n = True
                    nucleus += [ph]
                #we HAVE triggered nucleus but not coda bit + is V
                elif n and not c and ph.is_vowel():
                    nucleus += [ph]
                #we HAVE triggered nucleus but not coda bit + is V
                elif n and not c and ph.is_consonant():
                    c = True
                    coda += [ph]
                #nucleus and coda bit both triggered, all consonants now go in
                #coda
                elif n and c and ph.is_consonant():
                    coda += [ph]
                #this would mean multiple nuclei + the first part of this is
                #supposed to check for this!
                elif n and c and ph.is_vowel():
                    raise Exception("Vowel {} found in coda of {}".format(ph,self))
        else:
            #TODO idk
            pass
        return([onset,nucleus,coda])
                    
    def get_onset(self):
        return self.get_structure()[0]
    def get_nucleus(self):
        return self.get_structure()[1]
    def get_coda(self):
        return self.get_structure()[2]
    
    def get_rime(self):
        return self.get_nucleus() + self.get_coda()
        
    def is_open(self):
        if not self.get_coda():
            return True
        else:
            return False
            
    def is_closed(self):
        return not self.is_open()
    
    def has_clusters(self):
        if len(self.get_onset()) > 1 and len(self.get_coda()) > 1:
            return ["onset","coda"]
        elif len(self.get_onset()) > 1 and len(self.get_coda()) < 1:
            return ["onset"]
        elif len(self.get_onset()) < 1 and len(self.get_coda()) > 1:
            return ["coda"]
        else:
            return []

    def get_clusters(self):
        clusdict = {}
        if len(self.get_onset()) > 1:
            clusdict["onset"] = self.get_onset()
        if len(self.get_coda()) > 1:
            clusdict["coda"] = self.get_coda()
        return clusdict
        
    def has_polyphthong(self):
        if len(get_nucleus()) > 1:
            return True
        else:
            return False
    
    def get_polyphthong(self)
        if self.has_polyphthong:
            return self.get_nucleus()
        else:
            raise Exception("Syllable {} contains no polyphthong".format(self))

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