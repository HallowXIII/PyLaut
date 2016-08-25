from pylaut.phone import MonoPhone
import json

#what should a phonology store?

#PHONEMES, obviously -- a set of Phones as The Phonemic Vowels, from which allophonic
#+ suprasegmental variants are derived

#but also systems
# -- allophony
# -- suprasegmentals
# -- system analysis -- systemzwang

#Vowels
#------

#dhok has compiled a big list + classified vowel systems at http://www.incatena.org/viewtopic.php?f=7&t=41583
#classifying a collection of vowels like this would be a start

#something which goes 'lol ur vowels are the same as in <list of languages here>'
#this should be pretty easy, i think, since it is just looking at sets of vowels

#actually, get nort to consult, he is a vowelf*cker

#dipthongs????

#Consonants
#-----------

#?????

class Phoneme(MonoPhone):
    """
    Wrapper/decorator for Phones, containing extra information.
    """
    def __init__(self,ipa_string=None):
        super().__init__(ipa_string)
        self.subsystem = dict()
        
        self.JSON_OBJECT_NAME = "Phoneme"
        self.JSON_VERSION_NO = "pre-alpha-1"

    def __repr__(self):
        """
        The representation of a phoneme is the IPA symbol in slashes
        """
        return "/" + self.symbol + "/"
            
    def is_in_vowel_subsystem(self,subsystem):
        """
        Returns True if the Phoneme is in a vowel subsystem 'subsystem' 
        """
        if not self.is_vowel():
            raise Exception("{} is not a vowel, so cannot be in a vowel "
                            "subsystem '{}'.".format(self.symbol,subsystem))
        if subsystem in self.subsystem:
            return True
        else:
            return False
    
    def value_in_vowel_subsystem(self,subsystem):
        """
        If a Phoneme is in a vowel subsystem, returns the value (+-) of that Phoneme 
        in the subsystem
        """
        if not self.is_in_subsystem(subsystem):
            raise Exception("{} is not in subsystem "
                            "{}.".format(self.symbol,subsystem))
        else:
            return self.subsystem[subsystem]


class Phonology(object):
    """
    Refer to comments for inchoate comments.
    """
    def __init__(self, phonemes = [], phoneme_cls = Phoneme):
        self.phoneme_cls = phoneme_cls
        self.phonemes = {self.phoneme_cls(x) for x in phonemes}
        self.vowel_subsystems = dict()
        
        #between 0 and 1 -- please normalise
        self.onset_frequencies = _ONSET_FS = dict()
        self.nucleus_frequencies = _NUCLEUS_FS = dict()
        self.coda_frequencies = _CODA_FS = dict()
        
        self.JSON_OBJECT_NAME = "Phonology"
        self.JSON_VERSION_NO = "pre-alpha-1"

    def __repr__(self):
        return str(self.phonemes)

    def jdefault(self,o):
        """
        Turns some un-JSONable objects into JSONable ones
        """
        if isinstance(o,set):
            return list(o)
        if isinstance(o,self.phoneme_cls):
            return o.to_json()
            
    def to_json(self):
        return json.dumps(self.__dict__, default=self.jdefault)
    
    def restore_phoneme_set(self,json_list):
        """
        Several things in Phonology are stored as phoneme sets. This converts a
        JSONised phoneme set back into a proper one.
        """
        phoneme_set = set()
        for json_item in json_list:
            p = Phoneme()
            p.from_json(json_item)
            phoneme_set.add(p)
        return phoneme_set
            
    def from_json(self,json_phonology):
        pre_phonology = json.loads(json_phonology)

        #no need to restore object + version: this checks for that
        if "JSON_OBJECT_NAME" not in pre_phonology:
            raise Exception("JSON input malformed: no JSON_OBJECT_NAME given.")
        if pre_phonology["JSON_OBJECT_NAME"] != self.JSON_OBJECT_NAME:
            raise Exception("JSON type error: was "
            "given {}, should be {}.".format(pre_phonology["JSON_OBJECT_NAME"],
            self.JSON_OBJECT_NAME))
        if pre_phonology["JSON_VERSION_NO"] != self.JSON_VERSION_NO:
            raise Exception("JSON version error: was "
            "given {}, should be {}.".format(pre_phonology["JSON_VERSION_NO"],
            self.JSON_VERSION_NO))
            
        #restore main phoneme set
        self.phonemes = self.restore_phoneme_set(pre_phonology["phonemes"])
        
        #restore vowel subsystems dict
        pre_vowel_subsystems = {}
        if pre_phonology["vowel_subsystems"]:
            for key in pre_phonology["vowel_subsystems"]:
                pre_phoneme_set = pre_phonology["vowel_subsystems"][key]
                phoneme_set = self.restore_phoneme_set(pre_phoneme_set)
                pre_vowel_subsystems[key] = phoneme_set
        self.vowel_subsystems = pre_vowel_subsystems
        
        #restore frequency counts
        if "onset_frequencies" in pre_phonology:
            self.onset_frequencies = pre_phonology["onset_frequencies"]
        if "nucleus_frequencies" in pre_phonology:
            self.nucleus_frequencies = pre_phonology["nucleus_frequencies"]
        if "coda_frequencies" in pre_phonology:
            self.coda_frequencies = pre_phonology["coda_frequencies"]
            
    def add_phoneme(self,phoneme):
        """
        Add a Phoneme object to the Phonology
        """
        if type(phoneme) != phoneme_cls:
            raise TypeError("{} not a {} object".format(phoneme,
                                                        self.phoneme_cls))
        self.phonemes.add(phoneme)
        self.phoneme_frequencies[phoneme] = None
        
    def get_vowels(self):
        """
        Gets the subset of self.phonemes which are vowels
        """
        return {ph for ph in self.phonemes if ph.is_vowel()}
        
    def get_consonants(self):
        """
        Gets the subset of self.phonemes which are consonants
        """
        return {ph for ph in self.phonemes if ph.is_consonant()}
    
    def get_phoneme(self,ipa_str):
        """
        Return the Phoneme represented by ipa_str
        """
        our_phoneme = None
        for phoneme in self.phonemes:
            if phoneme.is_symbol(ipa_str):
                our_phoneme = phoneme
        if our_phoneme:
            return our_phoneme
        else:
            raise Exception("Phoneme /{}/ not found in Phonology.".format(ipa_str))
    
    def get_phonemes_with_feature(self,feature,value):
        """
        Returns subset of self.phonemes where the 'feature' is "+" or "-"
        """
        return set([ph for ph in self.phonemes if ph.feature_is(feature,value)])

    def get_phonemes_with_features(self,feature_dict):
        """
        Takes a dictionary of {feature:value...} pairs and returns the subset of 
        self.phonemes where these features are found
        """
        valid_ph = self.phonemes.copy()
        for feature, value in feature_dict.items():
            valid_ph = set([ph for ph in valid_ph if ph.feature_is(feature,value)])
        return valid_ph

    def get_phoneme_dictionary(self):
        """
        Return a dictionary {symbol:phoneme}
        """
        phoneme_dict = dict()
        for phoneme in self.phonemes:
            phoneme_dict[phoneme.symbol] = phoneme
        return phoneme_dict
    
    #phoneme frequency
    def set_phoneme_frequency_from_list(self,part,phoneme_list_list):
        """
        Given a [possibly long] list of lists of phonemes and a syllable part 
        (onset,nucleus,coda), updates self.----_frequencies with appropriate, 
        normalised values
        """
        mapdict = {
                   "onset":self.onset_frequencies,
                   "nucleus":self.nucleus_frequencies,
                   "coda":self.coda_frequencies,
                  }
                  
        freqdict = dict()
        for phoneme_list in phoneme_list_list:
            phoneme_string = "".join([ph.__repr__() for ph in phoneme_list])
            if phoneme_string in freqdict:
                freqdict[phoneme_string] += 1
            else:
                freqdict[phoneme_string] = 1
        
        total = sum(freqdict.values())
        normalised_freqdict = {k : v/total for k,v in freqdict.items()}
        if part == "onset":
            self.onset_frequencies = normalised_freqdict
        elif part == "nucleus":
            self.nucleus_frequencies = normalised_freqdict
        elif part == "coda":
            self.coda_frequencies = normalised_freqdict
        else:
            raise Exception("{} not a valid syllable part".format(part))
    
    def get_phoneme_frequency_total(self,phoneme):
        """
        Given a phoneme, returns the frequency of that phoneme, relative to all 
        phonemes. This counts phonemes in clusters as well.
        """
        if type(phoneme) != self.phoneme_cls:
            raise TypeError()
        totalfreq = 0
        for freqdict in [self.onset_frequencies,
                         self.nucleus_frequencies,
                         self.coda_frequencies]:
            for sequence in freqdict:
                #first condition is to skip null onsets,codas etcs
                if len(sequence) > 1 and phoneme.symbol in sequence:
                    totalfreq += freqdict[sequence]
        #each freqdict is normalised between 0 and 1. adding them up makes it
        #between 0 and 3, therefore this renormalises it
        
        #TODO check this gives the right answer
        return totalfreq/3
        
    #vowel subsystems
     
    def define_vowel_subsystem(self,feature,autoadd=False):
        """
        Defines a pair of vowel subsystems based on a feature.
        Usually 'length' or 'stress' but also allowing arbitrary 
        features, e.g. SE Asian '+-high' subsystem:
        c.f. http://www.incatena.org/viewtopic.php?p=1047560#p1047560
        
        'feature' can be an arbitrary string, but if it matches an actual 
        phonological feature, then vowels can be added to it automatically.
        You would want to do this if e.g. all your long vowels are [+long]. 
        You would not want to do it if they are english-type 'long vowels'
        
        """
        self.vowel_subsystems["+" + feature] = set()
        self.vowel_subsystems["-" + feature] = set()     
        
        if autoadd:
            #TODO check to see if feature actually is a feature
            
            #go through all vowels and check for 'feature', assigning to
            #appropriate subsystem as it goes
            our_vowels = self.get_vowels()
            for vowel in our_vowels:
                if vowel.feature_is_true(feature):
                    self.assign_vowel_to_subsystem(vowel,feature,"+")
                elif vowel.feature_is_false(feature):
                    self.assign_vowel_to_subsystem(vowel,feature,"-")
                else:
                    pass
        
    def assign_vowel_to_subsystem(self,v,subsystem,value):
        """
        Assigns a vowel phoneme 'v' to a subsystem defined by define_vowel_subsystem 
        with the feature 'feature' in the subsystem that is +- 'value'
        """
        #check v is a Phoneme
        if type(v) != self.phoneme_cls:
            raise Exception("Input '{}' not a {} object.\n"
                            "{} not valid type.".format(v,
                                                        self.phoneme_cls,
                                                        type(v)))
                    
        #check v is a vowel
        if not v.is_vowel():
            raise Exception("{} is not a vowel, so cannot be in a vowel "
                            "subsystem '{}'.".format(self.symbol,subsystem)) 
                                  
        #check the subsystem exists
        if "+" + subsystem not in self.vowel_subsystems:
            raise Exception("{} not a defined vowel subsystem".format(subsystem))
        
        #check the value is valid
        if value not in "+-":
            raise Exception("{} not a valid vowel subsystem value".format(value))
        
        #if they all check out, add it
        self.vowel_subsystems[value + subsystem].add(v)
        v.subsystem[subsystem] = value

    def get_vowels_in_subsystem(self,subsystem,value):
        """
        Returns a set of vowels such that they are of value ("+" or "-") in the 
        given subsystem.
        """
        return self.vowel_subsystems[value+subsystem]
        
    def get_vowel_subsystems(self):
        """
        Returns a list of the vowel subsystems defined in the phonology
        """
        subsystems = list(set([k[1:] for k in self.vowel_subsystems.keys()]))
        return subsystems
        
    def count_vowels(self):
        """
        Returns a dictionary giving the "total" number of vowels in the phonology 
        followed by a breakdown by subsystems, if any, in turn broken down by "+"
         or "-"
        """
        count_dict = dict()
        count_dict["total"] = len(self.get_vowels())
        subsystems = self.get_vowel_subsystems()
        for subsystem in subsystems:
            count_dict[subsystem] = {"+":None,"-":None}
            subp = len(self.get_vowels_in_subsystem(subsystem,"+"))
            subm = len(self.get_vowels_in_subsystem(subsystem,"-"))
            count_dict[subsystem]["+"], count_dict[subsystem]["-"] = subp, subm
        return count_dict
        
################################################################################

if __name__ == '__main__':
    vs = ["aː","iː","uː","a","i","u","ə"]
    
    cs = ["p","t","k","s","x","r","l","w"]
    
    ph = Phonology(vs+cs)

    print(ph.phonemes)
    
    ph.define_vowel_subsystem("long",autoadd=True)

    print(ph.vowel_subsystems)
    print(ph.get_phonemes_with_feature("voice","-"))
    fd = {"voice":"-","continuant":"-"}
    print(ph.get_phonemes_with_features(fd))
    
    j = ph.to_json()
    
    f = Phonology()
    f.from_json(j)
    print(f.get_phonemes_with_feature("voice","-"))
