from pylaut.language.phonology import phone, featureset


class MonoPhone(phone.Phone):
    """
    MonoPhones are Phones which use the MONOPHONE feature-set. For further
    information, please refer to Phone.
    """

    _FEATURE_SET_NAME = "monophone"

    _CONSONANTAL_FEATURE = "consonantal"
    _LO_V_FEATURE, _HI_V_FEATURE = "low", "high"
    _FR_V_FEATURE, _BA_V_FEATURE = "front", "back"
    _RO_V_FEATURE = "round"

    _VOI_C_FEATURE = "voice"

    _CONT_C_FEATURE = "continuant"
    _SON_C_FEATURE = "sonorant"

    _LAT_C_FEATURE = "lateral"
    _NAS_C_FEATURE = "nasal"

    def __init__(self, ipa_string=None):
        super().__init__(featureset.FeatureModel('monophone'), ipa_string)
        self.JSON_OBJECT_NAME = "Phone/MonoPhone"
        self.JSON_VERSION_NO = "MonoPhone-pre-alpha-1"
        if ipa_string:
            self.set_features_from_ipa(ipa_string)
            self.set_symbol_from_features()

    # interface compliance
    def is_tone(self):
        return False

    # vowel properties
    def is_vowel(self):
        if self.feature_is(MonoPhone._CONSONANTAL_FEATURE,
                           self.feature_model._FALSE_FEATURE):
            return True
        else:
            return False

    def is_low_vowel(self):
        if self.is_vowel() and self.feature_is(
                MonoPhone._LO_V_FEATURE, self.feature_model._TRUE_FEATURE):
            return True
        else:
            return False

    def is_high_vowel(self):
        if self.is_vowel() and self.feature_is(
                MonoPhone._HI_V_FEATURE, self.feature_model._TRUE_FEATURE):
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
        if self.is_vowel() and self.feature_is(
                MonoPhone._FR_V_FEATURE, self.feature_model._TRUE_FEATURE):
            return True
        else:
            return False

    def is_back_vowel(self):
        if self.is_vowel() and self.feature_is(
                MonoPhone._BA_V_FEATURE, self.feature_model._TRUE_FEATURE):
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
        if self.is_vowel() and self.feature_is(
                MonoPhone._RO_V_FEATURE, self.feature_model._TRUE_FEATURE):
            return True
        else:
            return False

    # consonant properties

    def is_consonant(self):
        if self.feature_is(MonoPhone._CONSONANTAL_FEATURE,
                           self.feature_model._TRUE_FEATURE):
            return True
        else:
            return False

    def is_voiced_consonant(self):
        if self.is_consonant() and self.feature_is(
                MonoPhone._VOI_C_FEATURE, self.feature_model._TRUE_FEATURE):
            return True
        else:
            return False

    def is_stop(self):
        if self.is_consonant() and self.feature_is(
                MonoPhone._CONT_C_FEATURE, self.feature_model._FALSE_FEATURE):
            return True
        else:
            return False

    def is_nasal_stop(self):
        if self.is_stop() and self.feature_is(
                MonoPhone._NAS_C_FEATURE, self.feature_model._TRUE_FEATURE):
            return True
        else:
            return False

    def is_approximant(self):
        if self.is_consonant():
            if self.feature_is(MonoPhone._CONT_C_FEATURE,
                               self.feature_model._TRUE_FEATURE):
                if self.feature_is(MonoPhone._SON_C_FEATURE,
                                   self.feature_model._TRUE_FEATURE):
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def is_lateral_approximant(self):
        if self.is_approximant() and self.feature_is(
                MonoPhone._LAT_C_FEATURE, self.feature_model._TRUE_FEATURE):
            return True
        else:
            return False

    def is_fricative(self):
        if self.is_consonant():
            if self.feature_is(MonoPhone._CONT_C_FEATURE,
                               self.feature_model._TRUE_FEATURE):
                if self.feature_is(MonoPhone._SON_C_FEATURE,
                                   self.feature_model._FALSE_FEATURE):
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
        # based on;
        # http://www.gial.edu/images/PDF/Parker%20dissertation.pdf
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
