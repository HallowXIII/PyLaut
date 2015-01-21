from phone import MonoPhone

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

#short + long vowel systems
#and vowel subsystems generally c.f. nort: http://www.incatena.org/viewtopic.php?p=1047560#p1047560

#actually, get nort to consult, he is a vowelf*cker

#dipthongs????

#Consonants
#-----------

#?????

class Phoneme(MonoPhone):
    """
    Wrapper/decorator for Phones, containing extra information.
    """
    
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
        
    def __init__(self,ipa_string=None):
        super().__init__(ipa_string)
        self.subsystem = dict()

    def __repr__(self):
        """
        The representation of a phoneme is the IPA symbol in slashes
        """
        return "/" + self.symbol + "/"
        
class Phonology(object):
    """
    Refer to comments for inchoate comments.
    """
    def __init__(self,phonemes=[]):
        self.phonemes = {Phoneme(x) for x in phonemes}
        self.vowel_subsystems = dict()
        
    def __repr__(self):
        return str(self.phonemes)

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
    
    #vowel subsystems
     
    def define_vowel_subsystem(self,feature,autoadd=False):
        """
        Defines a pair of vowel subsystems based on a feature.
        Usually 'length' or 'stress' but also allowing arbitrary 
        features, e.g. SE Asian '+-high' subsystem:
        c.f. http://www.incatena.org/viewtopic.php?p=1047560#p1047560
        
        'feature' can be an arbitrary string, but if it matches an actual 
        phonological feature, then vowels can be added to it automatically.
        
        you would want to do this if e.g. all your long vowels are [+long]. 
        you would not want to do it if they are english-type 'long vowels'
        
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
        if type(v) != Phoneme:
            raise Exception("Input '{}' not a Phoneme.\n"
                            "{} not valid type.".format(v,type(v)))
                    
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
