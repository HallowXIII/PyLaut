from pylaut.phone import MonoPhone
from pylaut.phonology import Phonology
from pylaut.utils import breakat, powerset
import itertools
import sys

class Syllable(object):

    def __init__(self,phonemes):
        self.phonemes = phonemes
        self.stressed = False
        self.word_position = None
        self.structure = None

    def __eq__(self, other):
        return repr(self) == repr(other)

    def __hash__(self):
        return self.__repr__().__hash__()

    def __iter__(self):
        for ph in self.phonemes:
            yield ph

    def to_json(self):
        pass
        
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
        return self.stressed
        
    def set_stressed(self):
        self.stressed = True
    
    def set_unstressed(self):
        self.stressed = False
        
    def set_word_position(self,position):
        if position not in ["initial","medial","final","monosyllable"]:
            raise ValueError()
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
            
    def find_nuclei(self):
        """
        Finds all possible nuclei in the syllable. So far, has problems
        dealing with things that aren"t easy and unambiguous.
        """
        sonorities = [(ph,ph.get_sonority()) for ph in self.phonemes]
        #check to see if there are phones w/ sonorities >= 10        
        if max(sonorities, key=lambda x: x[1])[1] >= 10:
            maximum_sonority = 10
        #reduce all vowels to level 10, n := 10
            sonorities = [(s[0],10) if s[1] > 10
                          else s for s in sonorities]
        #if there are none, check for sonorities >= 5 and use max as n
        elif max(sonorities, key=lambda x: x[1])[1] >= 5:
            maximum_sonority = max(sonorities, key=lambda x: x[1])[1]
        #if there are neither, return 0
        else:
            return []
        
        #group together all adjacent ns
        #TODO: fun fact: len(a) is too big, and a smaller value will work. find it
        for m in range(len(sonorities)):
            for i, n in enumerate(sonorities):
                if i > 0 and sonorities[i-1][1] == n[1]:
                    sonorities[i] = None
            sonorities = [x for x in sonorities if x]

        #return ns in the list
        return [x[0] for x in sonorities if x[1] == maximum_sonority]

    def count_nuclei(self):
        """
        Returns an estimated number of nuclei in this syllable.
        If the value is greater than 1, something is likely wrong, e.g. the source
        has been incorrectly syllabified. If it is less than 1 either something 
        is wrong, or you are in the PNW.
        """
        return len(self.find_nuclei())
    
    def get_structure(self):
        if self.structure is not None:
            return self.structure
        else:
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
                    #we haven"t triggered either nucleus or coda bit + is C
                    if not n and not c and ph.is_consonant():
                        onset += [ph]
                    #we haven"t triggered either nucleus or coda bit + is V
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
                nc = self.find_nuclei()[0]
                nucleus.append(nc)
                ncidx = self.phonemes.index(nc)
                onset = self.phonemes[:ncidx]
                coda = self.phonemes[ncidx:]

            self.structure = (onset,nucleus,coda)
            return self.structure
                    
    def get_onset(self):
        return self.get_structure()[0]

    def get_nucleus(self):
        return self.get_structure()[1]

    def get_coda(self):
        return self.get_structure()[2]
    
    def get_rime(self):
        return self.get_nucleus() + self.get_coda()

    def has_onset(self):
        return True if self.get_onset() else False
    
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

    def get_max_cluster_length(self):
        return max([len(v) for v in self.get_clusters().values()])
        
    def has_polyphthong(self):
        if len(get_nucleus()) > 1:
            return True
        else:
            return False
    
    def get_polyphthong(self):
        if self.has_polyphthong:
            return self.get_nucleus()
        else:
            raise ValueError("Syllable {} contains no polyphthong".format(self))

    def get_pattern(self):
        ptn = []
        onset, nucleus, coda = self.get_structure()
        for c in onset:
            ptn.append("C")
        for n in nucleus:
            if n.is_vowel():
                ptn.append("V")
            elif n.is_nasal_stop():
                ptn.append("N")
            else:
                ptn.append("R")
        for c in coda:
            ptn.append("C")

        return "".join(ptn)
                

class Word(object):
    def __init__(self,syllables):
        self.syllables = syllables
        self.phonemes = [syl.phonemes for syl in self.syllables]
        if len(self.syllables) > 1:
            self.syllables[0].set_word_position("initial")
            for syl in self.syllables[1:-1]:
                syl.set_word_position("medial")
            self.syllables[-1].set_word_position("final")
        else:
             self.syllables[0].set_word_position("monosyllable")
        
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

    def __iter__(self):
        for syl in self.syllables:
            yield syl


        
class WordFactory(object):
    """
    Makes Words.
    Needs to be initialised with a Phonology.
    make_words takes an IPA string, syllables delimited with <.> or <"> if stressed 
    and outputs a Word, composed of Syllables.
    """
    def __init__(self,phonology):
        self.phonology = phonology
        self.phoneme_dict = self.phonology.get_phoneme_dictionary()

    def mostlikely(self, lss, weightf=None):

        def default(syllable):
            wt = 0.0
            try:
                if syllable.has_onset():
                    wt += 0.6
                    if not syllable.is_open():
                        wt += 0.1
                elif syllable.is_closed():
                    wt += 0.1
                if not syllable.has_clusters():
                    wt += 0.7
                else:
                    if syllable.get_max_cluster_length() == 2:
                        wt += 0.3
                    if syllable.is_open():
                        wt += 0.2
                        
                return wt
            except Exception as e:
                return -10.0

        if weightf is None:
            weightf = default

        memo = {}
        def weight(syl):
            if syl not in memo:
                memo[syl] = weightf(syl)
            return memo[syl]

        candidates = map(lambda xs: list(map(self.make_syllable, xs)), lss)
        return max([(c, sum(map(weight, c))) for c in candidates],
                   key = lambda b: b[1])[0]
        
    def fromlist(self, seglist, weight=None):

        syls = []
        for breaks in powerset(range(1, len(seglist))):
            syls.append(breakat(seglist, breaks))

        return Word(self.mostlikely(syls, weight))
    

    def make_syllable(self, segs):
        proto_syl = []
        stressed = False
        if "ˈ" in segs:
            if segs[0] == "ˈ":
                stressed = True
                segs = segs[1:]
            else:
                return None
        for ipa_seg in segs:
            proto_syl += [self.phoneme_dict[ipa_seg].copy()]
        syl = Syllable(proto_syl)
        if stressed:
            syl.set_stressed()
        return syl
            

    def make_word(self, raw_word):
        #turn ' into .' to allow splitting into syllables
        #what about ˌ ?
        raw_word = raw_word.replace("'",".'")
        raw_syllables = [syl for syl in raw_word.split(".") if syl]
        syllables = []
        for rs in raw_syllables:
            syl = []
            stressed = False

            #if there is a "'", this syllable has stress
            if rs[0] == "'":
                stressed = True

            #TODO identify diacritics
            proto_syl = []

            if stressed:
                proto_rs = rs[1:]
            else:
                proto_rs = rs

            for ipa_char in proto_rs:
                proto_syl += [self.phoneme_dict[ipa_char].copy()]
            syl = Syllable(proto_syl)
            if stressed:
                syl.set_stressed()

            syllables += [syl]

        word = Word(syllables)
        return word

################################################################################

def test():
    
    #example phonology
    phonemes = ["p","t","k",
                "b","d","ɡ",
                "m","n",
                "s","f",
                "w","j","r","l",
                "a","e","i","o","u"]
    phonology = Phonology(phonemes)

    return WordFactory(phonology)


def main():
    #example phonology
    phonemes = ["p","t","k",
                "b","d","ɡ",
                "m","n",
                "s","f",
                "w","j",
                "r","l",
                "a","e","i","o","u"]
    phonology = Phonology(phonemes)

    wf = WordFactory(phonology)
    
    #raw_words = ["a'ma.re","'ka.sa","'ar.bo.re","et","ak'tjo.ne"]
    #words = []
    #for word in raw_words:
    #    words += [wf.make_word(word)]
    #print(words)

    raw_words = ["amare", "banana", "aktjone", "ndela", "adam", "erajnd"]
    print(list(map(wf.fromlist, raw_words)))

if __name__ == "__main__":
    main()
