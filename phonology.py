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
        
        
    def define_vowel_subsystem(self,feature):
        """
        Defines a pair of vowel subsystems based on a feature.
        Usually 'length' or 'stress' but also allowing arbitrary 
        features, e.g. SE Asian '+-high' subsystem:
        c.f. http://www.incatena.org/viewtopic.php?p=1047560#p1047560
        """
        self.vowel_subsystems["+" + feature] = set()
        self.vowel_subsystems["-" + feature] = set()     
        
        
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
        
        
        
if __name__ == '__main__':
    vs = ["aː","iː","uː","a","i","u","ə"]
    ls = ["+", "+", "+", "-","-","-","-"]
    
    ph = Phonology(vs)

    print(ph.phonemes)
    
    ph.define_vowel_subsystem("long")
    for v, l in zip(vs,ls):
        pv = ph.get_phoneme(v)
        ph.assign_vowel_to_subsystem(pv,"long",l)

    print(ph.vowel_subsystems)
