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

class Phonology(object):
    """
    Refer to comments for inchoate comments.
    """
    def get_vowels(self):
        return {ph for ph in self.phonemes if ph.is_vowel()}
        
    def get_consonants(self):
        return {ph for ph in self.phonemes if ph.is_consonant()}
        
    def __init__(self,phonemes=[]):
        self.phonemes = {x:None for x in phonemes}
        
        
        
if __name__ == '__main__':
    vs = [MonoPhone(vowel) for vowel in ["a","e","i","o","u","p","t","k"]]
    ph = Phonology(vs)
    for v in ph.get_vowels():
        print(v)
    for c in ph.get_consonants():
        print(c)
