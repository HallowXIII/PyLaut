import json
from copy import deepcopy

from pylaut.language.phonology import featureset


class Phone(object):
    """
    Phones are the atomic unit of PyLaut. They are somewhere between acoustic
    phones and phonemes.

    They are a collection [dictionary + canonical order] of phonological
    features with extra structure to make manipulating them easier.
    """

    @staticmethod
    def jdefault(o):
        if isinstance(o, featureset.FeatureModel):
            return o.to_json()

    def __init__(self, feature_model: featureset.FeatureModel, ipa_str=None):

        self.feature_model = feature_model

        # the features of the Phone
        self.features = dict()

        # representation of the Phone
        self.symbol = "0"

        if ipa_str:
            self.set_features_from_ipa(ipa_str)
            self.set_symbol_from_features()

        self.JSON_OBJECT_NAME = "Phone"
        self.JSON_VERSION_NO = "pre-alpha-1"

    def __repr__(self):
        """
        The representation of a phone is the IPA symbol in square brackets
        """
        return "[" + self.symbol + "]"

    def to_json(self):
        """
        Returns a JSON representation of the Phone
        """
        return json.dumps(self.__dict__, default=self.jdefault)

    def from_json(self, json_phone):
        """
        Reinitialise from JSON representation of the Phone
        """
        pre_phone = json.loads(json_phone)

        if "JSON_OBJECT_NAME" not in pre_phone:
            raise Exception("JSON input malformed: no JSON_OBJECT_NAME given.")
        if pre_phone["JSON_OBJECT_NAME"] != self.JSON_OBJECT_NAME:
            raise Exception("JSON type error: was "
                            "given {}, should be {}.".format(
                                pre_phone["JSON_OBJECT_NAME"],
                                self.JSON_OBJECT_NAME))
        if pre_phone["JSON_VERSION_NO"] != self.JSON_VERSION_NO:
            raise Exception("JSON version error: was "
                            "given {}, should be {}.".format(
                                pre_phone["JSON_VERSION_NO"],
                                self.JSON_VERSION_NO))

        self.__dict__ = pre_phone

    def print_feature_list(self):
        """
        Produce a feature string from the Phone,
        e.g. [-syllabic] [+consonantal] [-continuant] [+sonorant] ...
        """
        output = []
        for feature in self.feature_model.features:
            if self.features[feature] == self.feature_model._TRUE_FEATURE:
                output += ["[+{}]".format(feature)]
            elif self.features[feature] == self.feature_model._FALSE_FEATURE:
                output += ["[-{}]".format(feature)]
            else:
                pass

        return output

    def clear_features(self):
        """
        Clears the entries of self.features.
        """
        self.features = {x: None for x in self.features}

    def set_feature(self, feature_name, feature_value):
        """
        Sets the feature_name of the Phone to value feature_quality
        This ought not to be used directly, instead use
        set_feature_true/false/null()
        """
        if not self.feature_model:
            raise Exception("Phone does not have a feature set initialised!")
        else:
            if feature_name not in self.feature_model.features:
                raise Exception("Feature '{}' not found in Phone's "
                                "feature set".format(feature_name))
            elif (feature_value not in self.feature_model.
                  _possible_feature_values):
                raise Exception("'{}' not a valid value for feature in "
                                "Phone".format(feature_value))
            else:
                # do it
                self.features[feature_name] = feature_value

    def set_features_to_values(self, feature_names, values):
        for f, v in zip(feature_names, values):
            self.set_feature(f, v)

    def set_features_bool(self, feature_names, hey_boo):
        """
        Used by set_features_true/false/null
        hey_boo is the object that the feature is set to
        """
        # in case we are passed a string and not a list, so the loop can
        # iterate through it properly
        if isinstance(feature_names, str):
            feature_names = [feature_names]

        for feature_name in feature_names:
            self.set_feature(feature_name, hey_boo)

    def set_features_true(self, feature_names):
        """
        Sets the feature_name of the Phone to be true/+
        """
        self.set_features_bool(feature_names, self.feature_model._TRUE_FEATURE)

    def set_features_false(self, feature_names):
        """
        Sets the feature_name of the Phone to be false/-
        """
        self.set_features_bool(feature_names,
                               self.feature_model._FALSE_FEATURE)

    def set_features_null(self, feature_names):
        """
        Sets the feature_name of the Phone to be null/0
        """
        self.set_features_bool(feature_names, self.feature_model._NULL_FEATURE)

    def set_features_from_ipa(self, ipa_str):
        """
        Takes Unicode IPA symbol (optionally with diacritics) and
        automagically assigns appropriate featural values to Phone
        """
        ipa_char_features = self.feature_model.get_features_from_ipa(ipa_str)

        # clear the features dict to prepare for the IPA data [which should be
        # complete + contain a value for all features]
        self.clear_features()
        self.set_features_to_values(self.feature_model.features,
                                    ipa_char_features)

    def get_feature_list(self):
        """
        Returns a list of the values of features from self.features, using the
        canonical order from self.feature_set.
        """
        feature_list = list()
        for feature in self.feature_model.features:
            feature_list += [self.features[feature]]
        return feature_list

    def feature_is(self, feature, hey_boo):
        """
        Returns True if the feature 'feature' in the phone is hey_boo,
        otherwise returns False
        """
        if not self.feature_model.is_good_feature(feature):
            raise Exception("{} not a valid feature.".format(feature))
        else:
            if hey_boo not in self.feature_model._possible_feature_values:
                raise Exception(
                    "{} not a valid feature value.".format(hey_boo))
            else:
                if (self.features[feature]) == hey_boo:
                    return True
                else:
                    return False

    def feature_is_true(self, feature):
        if self.feature_is(feature, self.feature_model._TRUE_FEATURE):
            return True
        else:
            return False

    def feature_is_false(self, feature):
        if self.feature_is(feature, self.feature_model._FALSE_FEATURE):
            return True
        else:
            return False

    def feature_is_null(self, feature):
        if self.feature_is(feature, self.feature_model._NULL_FEATURE):
            return True
        else:
            return False

    def set_symbol_from_features(self):
        """
        Sets self.symbol using get_ipa_from_features
        """
        self.symbol = self.feature_model.get_ipa_from_features(
            self.get_feature_list())

    def is_symbol(self, ipa_string):
        if self.symbol == ipa_string:
            return True
        else:
            return False

    def copy(self):
        return deepcopy(self)


class MonoPhone(Phone):
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
