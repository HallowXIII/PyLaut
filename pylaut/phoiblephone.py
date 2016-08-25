from pylaut.phone import Phone
from os import path

class PhoiblePhone(Phone):
    """
    PhoiblePhones are Phones which use the MONOPHONE feature-set. For further 
    information, please refer to Phone.
    """
    
    _FEATURE_SET_NAME = "phoible-segf"
        
    _CONSONANTAL_FEATURE = "consonantal"
    _LO_V_FEATURE, _HI_V_FEATURE = "low","high"
    _FR_V_FEATURE, _BA_V_FEATURE = "front","back"
    _RO_V_FEATURE = "round"
    
    _VOI_C_FEATURE = "periodicGlottalSource"
    
    _CONT_C_FEATURE = "continuant"
    _SON_C_FEATURE = "sonorant"
    
    _LAT_C_FEATURE = "lateral"
    _NAS_C_FEATURE = "nasal"

    _SYL_FEATURE = "syllabic"

    def get_ipa_from_features(self):
        """
        Returns an IPA symbol if the Phone fits an IPA symbol in the feature-
        set used, requiring no diacritics, and None otherwise.
        """
        matching_symbols = list()
        our_feature_list = self.get_feature_list()
        for ipa_char in self._feature_set_ipa_dict:
            if self._feature_set_ipa_dict[ipa_char] == our_feature_list:
                matching_symbols += [ipa_char]
        
        if len(matching_symbols) < 1:
            return None
        else:
            return matching_symbols[0]

    def set_features_from_ipa(self,ipa_str):
        """
        Takes Unicode IPA symbol (optionally with diacritics) and automagically assigns appropriate featural 
        values to Phone
        """

        def flookup(self, ipa_str):

            if len(ipa_str) == 0:
                return

            if (ipa_str not in self._feature_set_ipa_dict and
                ipa_str[-1] in self._feature_set_ipa_diacritics):
                flookup(self, ipa_str[:-1])
                try:
                    char = ipa_str[-1]
                    for featstr in self._feature_set_ipa_diacritics[char]:
                        dc_feat = featstr[1:]
                        dc_val =  featstr[0]

                        if dc_val == Phone._TRUE_FEATURE:
                            self.set_features_true(dc_feat)
                        elif dc_val == Phone._FALSE_FEATURE:
                            self.set_features_false(dc_feat)
                        else:
                            self.seat_features_null(dc_feat)

                except KeyError:
                    raise KeyError(" {}  not found in IPA lookup.".format(char))

            else:

                ipa_char_features = self._feature_set_ipa_dict[ipa_str]

                for ipa_feat, our_feat in zip(ipa_char_features,
                                              self.feature_set):
                    if ipa_feat == Phone._TRUE_FEATURE:
                        self.set_features_true(our_feat)
                    elif ipa_feat == Phone._FALSE_FEATURE:
                        self.set_features_false(our_feat)
                    else:
                        self.set_features_null(our_feat)

        #clear the features dict to prepare for the IPA data [which should be
        #complete + contain a value for all features]
        self.clear_features()

        flookup(self, ipa_str)
        
    #vowel properties
    def is_vowel(self):
        if self.feature_is(PhoiblePhone._SYL_FEATURE,
                           PhoiblePhone._TRUE_FEATURE):
            return True
        else:
            return False
    
    def is_low_vowel(self):
        if self.is_vowel() and self.feature_is(PhoiblePhone._LO_V_FEATURE,
                                               PhoiblePhone._TRUE_FEATURE):
            return True
        else:
            return False

    def is_high_vowel(self):
        if self.is_vowel() and self.feature_is(PhoiblePhone._HI_V_FEATURE,
                                               PhoiblePhone._TRUE_FEATURE):
            return True
        else:
            return False
    
    def is_mid_vowel(self):
        if (self.is_vowel() and not self.is_low_vowel() 
            and not self.is_high_vowel()):
            return True
        else:
            return False

    def is_front_vowel(self):
        if self.is_vowel() and self.feature_is(PhoiblePhone._FR_V_FEATURE,
                                               PhoiblePhone._TRUE_FEATURE):
            return True
        else:
            return False

    def is_back_vowel(self):
        if self.is_vowel() and self.feature_is(PhoiblePhone._BA_V_FEATURE,
                                               PhoiblePhone._TRUE_FEATURE):
            return True
        else:
            return False
    
    def is_central_vowel(self):
        if (self.is_vowel() and not self.is_front_vowel() 
            and not self.is_back_vowel()):
            return True
        else:
            return False
    
    def is_rounded_vowel(self):
        if self.is_vowel() and self.feature_is(PhoiblePhone._RO_V_FEATURE,
                                               PhoiblePhone._TRUE_FEATURE):
            return True
        else:
            return False
    
    #consonant properties
                  
    def is_consonant(self):
        if self.feature_is(PhoiblePhone._SYL_FEATURE,
                           PhoiblePhone._FALSE_FEATURE):
            return True
        else:
            return False

    def is_voiced_consonant(self):
        if self.is_consonant() and self.feature_is(PhoiblePhone._VOI_C_FEATURE,
                                                   PhoiblePhone._TRUE_FEATURE):
            return True
        else:
            return False

    def is_stop(self):
        if self.is_consonant() and self.feature_is(PhoiblePhone._CONT_C_FEATURE,
                                                   PhoiblePhone._FALSE_FEATURE):
            return True
        else:
            return False
    
    def is_nasal_stop(self):
        if self.is_stop() and self.feature_is(PhoiblePhone._NAS_C_FEATURE,
                                              PhoiblePhone._TRUE_FEATURE):
            return True
        else:
            return False
            
    def is_approximant(self):
        if self.is_consonant():
            if self.feature_is(PhoiblePhone._CONT_C_FEATURE,
                               PhoiblePhone._TRUE_FEATURE):
                if self.feature_is(PhoiblePhone._SON_C_FEATURE,
                                   PhoiblePhone._TRUE_FEATURE):
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
                
    def is_lateral_approximant(self):
        if self.is_approximant() and self.feature_is(PhoiblePhone._LAT_C_FEATURE,
                                                     PhoiblePhone._TRUE_FEATURE):
            return True
        else:
            return False
    
    def is_fricative(self):
        if self.is_consonant():
            if self.feature_is(PhoiblePhone._CONT_C_FEATURE,
                               PhoiblePhone._TRUE_FEATURE):
                if self.feature_is(PhoiblePhone._SON_C_FEATURE,
                                   PhoiblePhone._FALSE_FEATURE):
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
                      
    def get_sonority(self):
        """
        Returns an integer giving a rough quantification of the sonority of the
         phone. 10 or greater is a vowel; laterals are 8, other approximants are 
         9; nasals are 5, everything else is lower. 
        """
        #based on;
        #http://www.gial.edu/images/PDF/Parker%20dissertation.pdf
        if self.is_vowel():
            if self.is_central_vowel():
                return 10
            elif self.is_low_vowel():
                return 13
            elif self.is_mid_vowel():
                return 12
            elif self.is_high_vowel():
                return 11
            else:
                return -1
        else:
            if self.is_lateral_approximant():
                return 8
            elif self.is_approximant():
                return 9
            elif self.is_nasal_stop():
                return 5
            elif self.is_fricative() and self.is_voiced_consonant():
                return 3
            elif self.is_fricative() and not self.is_voiced_consonant():
                return 2
            elif self.is_stop() and self.is_voiced_consonant():
                return 2    
            elif self.is_stop() and not self.is_voiced_consonant():
                return 0
            else:
                return -1

    def __init__(self,ipa_string=None):
        super().__init__()
        self.JSON_OBJECT_NAME = "Phone/PhoiblePhone"
        self.JSON_VERSION_NO = "PhoiblePhone-pre-alpha-1"
        self.load_set_feature_set(self.feature_set_filename())
        if ipa_string:
            self.set_features_from_ipa(ipa_string)
            self.symbol = ipa_string


class PhoiblePhoneme(PhoiblePhone):
    """
    Wrapper/decorator for Phones, containing extra information.
    """
    def __init__(self,ipa_string=None):
        super().__init__(ipa_string)
        self.subsystem = dict()
        
        self.JSON_OBJECT_NAME = "PhoiblePhoneme"
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
