import json
from copy import deepcopy
from os import path
from pprint import pprint

import pylaut.utils as utils


class Phone(object):
    """
    Phones are the atomic unit of PyLaut. They are somewhere between acoustic
    phones and phonemes.

    They are a collection [dictionary + canonical order] of phonological
    features with extra structure to make manipulating them easier.
    """
    # the values features can take.
    _TRUE_FEATURE = "+"
    _FALSE_FEATURE = "-"
    _NULL_FEATURE = "0"
    _possible_feature_values = [_TRUE_FEATURE, _FALSE_FEATURE, _NULL_FEATURE]

    _FEATURE_SET_NAME = None
    # stores whether the feature set defines an IPA lookup table
    _FEATURE_SET_IPA_LOOKUP = False
    _feature_set_ipa_dict = dict()
    _feature_set_ipa_diacritics = dict()
    # the longest distance between features that get_ipa_from_features will
    # regard
    _IGNORE_DISTANCE_GREATER_THAN = 5

    def __init__(self, ipa_str=None):

        self.feature_set_name = None

        # the features of the Phone
        self.features = dict()
        # self.feature_set is a canonical order for features
        self.feature_set = list()

        # representation of the Phone
        self.symbol = "0"

        if ipa_str:
            self.set_features_from_ipa(ipa_str)

        self.JSON_OBJECT_NAME = "Phone"
        self.JSON_VERSION_NO = "pre-alpha-1"

    def __repr__(self):
        """
        The representation of a phone is the IPA symbol in square brackets
        """
        return "[" + self.symbol + "]"

    def feature_set_filename(self, dirname=None):
        if dirname is None:
            here = path.join(
                path.abspath(path.dirname(__file__)), '../../data/')
        else:
            here = dirname
        return path.join(here, self._FEATURE_SET_NAME)

    def to_json(self):
        """
        Returns a JSON representation of the Phone
        """
        return json.dumps(self.__dict__)

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
        for feature in self.feature_set:
            if self.features[feature] == Phone._TRUE_FEATURE:
                output += ["[+{}]".format(feature)]
            elif self.features[feature] == Phone._FALSE_FEATURE:
                output += ["[-{}]".format(feature)]
            else:
                pass

        return output

    def load_set_feature_set(self, feature_set_file_name):
        """
        Loads a feature set from file, sets the Phone's feature set to it and
        reinits self.features !! clearing any existing features !!

        A feature set file is a plain text file, with the name of the feature
        set on the first line, with features given in []s each on its separate
        line.
        """
        feature_set_raw = open(feature_set_file_name, "r").read().splitlines()
        feature_set_name = feature_set_raw[0]
        if feature_set_raw[1]:
            if feature_set_raw[1] and feature_set_raw[2] != "0":
                here = path.abspath(path.dirname(feature_set_file_name))
                Phone._FEATURE_SET_IPA_LOOKUP = True
                feature_set_ipa_filename = path.join(here, feature_set_raw[1])
                feature_set_diacritics_filename = path.join(
                    here, feature_set_raw[2])
        feature_set = [
            line for line in feature_set_raw
            if line and line[0] == "[" and line[-1] == "]"
        ]
        feature_set = [line[1:-1] for line in feature_set]

        # assign properties
        self.feature_set_name = feature_set_name
        self.feature_set = feature_set
        self.features = {x: None for x in self.feature_set}
        # does the feature set specify ipa lookup?
        if Phone._FEATURE_SET_IPA_LOOKUP and not Phone._feature_set_ipa_dict:
            try:
                feature_set_ipa_vals_file = open(feature_set_ipa_filename, "r")
                feature_set_ipa_vals_raw = feature_set_ipa_vals_file.read(
                ).splitlines()
                feature_set_ipa_vals_file.close()
            except IOError:
                raise Exception("Invalid IPA lookup file!")
            for line in feature_set_ipa_vals_raw[1:]:
                if line:
                    feature_set_ipa_val = line.split()
                    feats = [
                        features for features in
                        feature_set_ipa_val[1:len(feature_set_ipa_val)]
                    ]
                    Phone._feature_set_ipa_dict[feature_set_ipa_val[0]] = feats
            if not Phone._feature_set_ipa_diacritics:
                try:
                    feature_set_ipa_dcs_file = open(
                        feature_set_diacritics_filename, "r")
                    feature_set_ipa_dcs_raw = feature_set_ipa_dcs_file.read(
                    ).splitlines()
                    feature_set_ipa_dcs_file.close()
                except IOError as e:
                    raise Exception("Invalid IPA Diacritic lookup file! "
                                    "{}".format(e))
            for line in feature_set_ipa_dcs_raw[1:]:
                if line:
                    feature_set_ipa_dc = line.split()
                    # this is a more natural notation for a feature
                    # also the notation that get_ipa_from_features uses
                    Phone._feature_set_ipa_diacritics[
                        feature_set_ipa_dc[0]] = frozenset(
                            feature_set_ipa_dc[1:])

    def clear_features(self):
        """
        Clears the entries of self.features.
        """
        self.features = {x: None for x in self.feature_set}

    def set_feature(self, feature_name, feature_value):
        """
        Sets the feature_name of the Phone to value feature_quality
        This ought not to be used directly, instead use
        set_feature_true/false/null()
        """
        if not self.feature_set_name:
            raise Exception("Phone does not have a feature set initialised!")
        else:
            if feature_name not in self.features:
                raise Exception("Feature '{}' not found in Phone's "
                                "feature set".format(feature_name))
            elif feature_value not in Phone._possible_feature_values:
                raise Exception("'{}' not a valid value for feature in "
                                "Phone".format(feature_value))
            else:
                # do it
                self.features[feature_name] = feature_value

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
        self.set_features_bool(feature_names, Phone._TRUE_FEATURE)

    def set_features_false(self, feature_names):
        """
        Sets the feature_name of the Phone to be false/-
        """
        self.set_features_bool(feature_names, Phone._FALSE_FEATURE)

    def set_features_null(self, feature_names):
        """
        Sets the feature_name of the Phone to be null/0
        """
        self.set_features_bool(feature_names, Phone._NULL_FEATURE)

    def set_features_from_ipa(self, ipa_str):
        """
        Takes Unicode IPA symbol (optionally with diacritics) and
        automagically assigns appropriate featural values to Phone
        """
        ipa_char_features = Phone._feature_set_ipa_dict[ipa_str[0]]

        # clear the features dict to prepare for the IPA data [which should be
        # complete + contain a value for all features]
        self.clear_features()

        for ipa_feat, our_feat in zip(ipa_char_features, self.feature_set):
            if ipa_feat == Phone._TRUE_FEATURE:
                self.set_features_true(our_feat)
            elif ipa_feat == Phone._FALSE_FEATURE:
                self.set_features_false(our_feat)
            else:
                self.set_features_null(our_feat)
        if len(ipa_str) > 1:
            for char in ipa_str[1:]:
                try:
                    dc_feats = Phone._feature_set_ipa_diacritics[char]
                    for feat in dc_feats:
                        dc_feat = feat[1:]
                        dc_val = feat[0]
                        if dc_val == Phone._TRUE_FEATURE:
                            self.set_features_true(dc_feat)
                        elif dc_val == Phone._FALSE_FEATURE:
                            self.set_features_false(dc_feat)
                        else:
                            self.set_features_null(dc_feat)
                except KeyError:
                    raise KeyError(
                        " {}  not found in IPA lookup.".format(char))

    def feature_hamming(self, feature_list, ipa_feature_list):
        """
        Takes in two lists of features, from the same feature set + in same
        canonical order, in the order of 'arbitrary feature list' and 'ipa
        feature list' [or some other 'more canonical' feature list in case
        of reuse] and returns a tuple:
         (which features feature_list has different from ipa_feature_list,
          length of this list == hamming distance between the two)
        """
        distant_symbols = list()
        for i, (our, ipa) in enumerate(zip(feature_list, ipa_feature_list)):
            if our != ipa:
                distant_symbols += [our + self.feature_set[i]]

        return (distant_symbols, len(distant_symbols))

    def get_feature_list(self):
        """
        Returns a list of the values of features from self.features, using the
        canonical order from self.feature_set.
        """
        feature_list = list()
        for feature in self.feature_set:
            feature_list += [self.features[feature]]
        return feature_list

    def is_good_feature(self, feature):
        if feature in self.feature_set:
            return True
        else:
            return False

    def feature_is(self, feature, hey_boo):
        """
        Returns True if the feature 'feature' in the phone is hey_boo,
        otherwise returns False
        """
        if not self.is_good_feature(feature):
            raise Exception("{} not a valid feature.".format(feature))
        else:
            if hey_boo not in Phone._possible_feature_values:
                raise Exception(
                    "{} not a valid feature value.".format(hey_boo))
            else:
                if (self.features[feature]) == hey_boo:
                    return True
                else:
                    return False

    def feature_is_true(self, feature):
        if self.feature_is(feature, Phone._TRUE_FEATURE):
            return True
        else:
            return False

    def feature_is_false(self, feature):
        if self.feature_is(feature, Phone._FALSE_FEATURE):
            return True
        else:
            return False

    def feature_is_null(self, feature):
        if self.feature_is(feature, Phone._NULL_FEATURE):
            return True
        else:
            return False

    def is_good_ipa(self):
        """
        Returns an IPA symbol if the Phone fits an IPA symbol in the feature-
        set used, requiring no diacritics, and None otherwise.
        """
        matching_symbols = list()
        our_feature_list = self.get_feature_list()
        for ipa_char in Phone._feature_set_ipa_dict:
            if Phone._feature_set_ipa_dict[ipa_char] == our_feature_list:
                matching_symbols += [ipa_char]

        if len(matching_symbols) > 1:
            raise Exception("Multiple symbols match Phone: check feature set "
                            "for non-contrasting symbols.")
        elif len(matching_symbols) < 1:
            return None
        else:
            return matching_symbols[0]

    def set_symbol_from_features(self):
        """
        Sets self.symbol using get_ipa_from_features
        """
        self.symbol = self.get_ipa_from_features()

    def get_ipa_from_features(self):
        """
        Returns a string giving an IPA representation of the Phone.
        """
        # check to see if the phone has a good IPA representation first
        symbol = self.is_good_ipa()
        # if it does, return it
        if symbol:
            return symbol
        # otherwise proceed: we must identify a similar base IPA glyph and then
        # add diacritics
        # get feature list to compare to Phone._feature_set_ipa_dict
        our_feature_list = self.get_feature_list()
        # stores (features differing, # of different features = hamming dist)
        # indexed by ipa char
        hamming_dict = dict()

        for ipa_char in Phone._feature_set_ipa_dict:
            ipa_feature_list = Phone._feature_set_ipa_dict[ipa_char]
            diffs, hamming_dist = self.feature_hamming(our_feature_list,
                                                       ipa_feature_list)
            # ignore ipa symbols infeasibly far -- they are unlikely to make
            # good representations
            if hamming_dist > Phone._IGNORE_DISTANCE_GREATER_THAN:
                pass
            else:
                hamming_dict[ipa_char] = (diffs, hamming_dist)

        # compile a list from hamming_dict, sorting by hamming_dist
        hamming_list = sorted(hamming_dict.items(), key=lambda x: x[1][1])

        # collect items in hamming_list together into a dictionary
        # index is hamming distance between phone and base ipa chars
        # values are lists of tuples (ipa char, diffs)
        # these are our first-round candidates
        hamming_dict_collected = dict()
        for symbol, (diffs, distance) in hamming_list:
            if distance in hamming_dict_collected:
                hamming_dict_collected[distance] += [(symbol, diffs)]
            else:
                hamming_dict_collected[distance] = [(symbol, diffs)]

        # look to see which of these can have diacritics added and work out
        # which

        # reverse Phone._feature_set_ipa_diacritics so we can look up
        # diacritics from the feature
        reverse_diacritics = {
            a: b
            for b, a in Phone._feature_set_ipa_diacritics.items()
        }

        # this will hold our final candidates
        valid = list()

        # go through our first-round candidates
        for distance in hamming_dict_collected:
            for candidate_base, diffs in hamming_dict_collected[distance]:
                # every feature in the first-round candidates is checked to see
                # if there is a diacritic, if there is we note what the
                # diacritic is, otherwise we leave an ominous blank
                # purged_diffs = [reverse_diacritics[tuple(db)] if
                #                tuple(db) in reverse_diacritics else
                #                None for db in utils.breakat(
                #                    diffs, utils.powerset(range(
                #                        1, len(diffs))))]

                for brk in utils.powerset(range(1, len(diffs))):
                    purged_diffs = list()
                    for db in utils.breakat(diffs, brk):
                        try:
                            purged_diffs.append(
                                reverse_diacritics[frozenset(db)])
                        except KeyError:
                            purged_diffs.append(None)

                    if None in purged_diffs:
                        pass
                    else:
                        # we store the second-round candidate base glyph with
                        # diacritics
                        valid += [(candidate_base, purged_diffs)]

        # TODO: identify the lowest-indexed solutions thus left
        #      if it is unique, use that, otherwise I D K
        # for now we pick the first one, if there are any...
        if len(valid) < 1:
            raise Exception("No IPA representation found for Phone!")
        else:
            final_choice = valid[0]

        final_glyph = final_choice[0] + "".join(final_choice[1])
        return final_glyph

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

    # interface compliance
    def is_tone(self):
        return False

    # vowel properties
    def is_vowel(self):
        if self.feature_is(MonoPhone._CONSONANTAL_FEATURE,
                           MonoPhone._FALSE_FEATURE):
            return True
        else:
            return False

    def is_low_vowel(self):
        if self.is_vowel() and self.feature_is(MonoPhone._LO_V_FEATURE,
                                               MonoPhone._TRUE_FEATURE):
            return True
        else:
            return False

    def is_high_vowel(self):
        if self.is_vowel() and self.feature_is(MonoPhone._HI_V_FEATURE,
                                               MonoPhone._TRUE_FEATURE):
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
        if self.is_vowel() and self.feature_is(MonoPhone._FR_V_FEATURE,
                                               MonoPhone._TRUE_FEATURE):
            return True
        else:
            return False

    def is_back_vowel(self):
        if self.is_vowel() and self.feature_is(MonoPhone._BA_V_FEATURE,
                                               MonoPhone._TRUE_FEATURE):
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
        if self.is_vowel() and self.feature_is(MonoPhone._RO_V_FEATURE,
                                               MonoPhone._TRUE_FEATURE):
            return True
        else:
            return False

    # consonant properties

    def is_consonant(self):
        if self.feature_is(MonoPhone._CONSONANTAL_FEATURE,
                           MonoPhone._TRUE_FEATURE):
            return True
        else:
            return False

    def is_voiced_consonant(self):
        if self.is_consonant() and self.feature_is(MonoPhone._VOI_C_FEATURE,
                                                   MonoPhone._TRUE_FEATURE):
            return True
        else:
            return False

    def is_stop(self):
        if self.is_consonant() and self.feature_is(MonoPhone._CONT_C_FEATURE,
                                                   MonoPhone._FALSE_FEATURE):
            return True
        else:
            return False

    def is_nasal_stop(self):
        if self.is_stop() and self.feature_is(MonoPhone._NAS_C_FEATURE,
                                              MonoPhone._TRUE_FEATURE):
            return True
        else:
            return False

    def is_approximant(self):
        if self.is_consonant():
            if self.feature_is(MonoPhone._CONT_C_FEATURE,
                               MonoPhone._TRUE_FEATURE):
                if self.feature_is(MonoPhone._SON_C_FEATURE,
                                   MonoPhone._TRUE_FEATURE):
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def is_lateral_approximant(self):
        if self.is_approximant() and self.feature_is(MonoPhone._LAT_C_FEATURE,
                                                     MonoPhone._TRUE_FEATURE):
            return True
        else:
            return False

    def is_fricative(self):
        if self.is_consonant():
            if self.feature_is(MonoPhone._CONT_C_FEATURE,
                               MonoPhone._TRUE_FEATURE):
                if self.feature_is(MonoPhone._SON_C_FEATURE,
                                   MonoPhone._FALSE_FEATURE):
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

    def __init__(self, ipa_string=None):
        super().__init__()
        self.JSON_OBJECT_NAME = "Phone/MonoPhone"
        self.JSON_VERSION_NO = "MonoPhone-pre-alpha-1"
        self.load_set_feature_set(self.feature_set_filename())
        if ipa_string:
            self.set_features_from_ipa(ipa_string)
            self.set_symbol_from_features()


###############################################################################
# DEBUGGING
###############################################################################

if __name__ == "__main__":
    lol = MonoPhone()
    lol.set_features_from_ipa("m")
    lol.set_features_false("voice")
    lol.set_symbol_from_features()
    print(lol.symbol)
    # how nice, it works and prints m̥ :)))
    lol.set_features_from_ipa("ɡ")
    lol.set_features_false("voice")
    lol.set_symbol_from_features()
    print(lol.symbol)
    lol.set_features_from_ipa("q")
    lol.set_features_true("aspirated")
    lol.set_symbol_from_features()
    print(lol.symbol)
    # everything works! propose unification of +aspirate with +breathy
    # will get on a diacritic rewriter later
    lol.set_features_from_ipa("tˤʰ")
    pprint(lol.features)
    # yep, also this

    rofl = lol.to_json()
    pprint(rofl)

    nong = MonoPhone()
    nong.from_json(rofl)
    print(nong.symbol)
    nong.set_features_from_ipa("l")
    pprint(nong.features)
