class Phone(object):

    #TODO will read this from a config file
    def get_consonant_features(self):
        consonant_features =  {
                          "poa":0,
                          "articulation":0
                          }
        return consonant_features
           
    def get_vowel_features(self):
        vowel_features =  {
                          "height":0,
                          "open":0
                          }
        return vowel_features
                                   
    def is_consonant(self):  
        if type(self).__name__ == "Consonant":
            return True
        else:
            return False
            
    def is_vowel(self):  
        if type(self).__name__ == "Vowel":
            return True
        else:
            return False
    
    def set_features_from_ipa(self,ipa_char):
        """
        Takes Unicode IPA symbol and automagically assigns appropriate featural 
        values to Phone
        """
        pass
    
    def set_feature(self,feature_name,feature_quality):
        """
        Sets the feature_name of the Phone to value feature_quality
        """
        pass
    
    def init_feature_dict(self):
        """
        Initialises a blank features dictionary depending on the subtype
        """
        if self.is_vowel:
            print("I'm a vowel!")
            d = self.get_vowel_features()
        elif self.is_consonant:
            print("I'm a consonant!")
            d = self.get_consonant_features()
        else:
            print("I'm a mistake!")
            d = self.features
        self.features = {x:d[x] for x in d} 
                    
    def __init__(self):
        self.features = dict()
        self.is_vowel, self.is_consonant = False, False

class Vowel(Phone):
    def __init__(self):
        super().__init__()
        self.is_vowel = True

class Consonant(Phone):
    def __init__(self):
        super().__init__()
        self.is_consonant = True
        
lol = Vowel()
lol.init_feature_dict()

lel = Consonant()
lel.init_feature_dict()
print(lol.features)
print(lel.features)
