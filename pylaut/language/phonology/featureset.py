"""
Module defining a class to handle featural models. This functionality is needed
for basically all tasks performed by the package, so this module is quite
important, if not very glamorous, as it performs the unloved and thankless task
of providing basic infrastructure.
"""

import json
import pathlib
import pkgutil
from typing import List, Optional, Tuple, Dict, Any
import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

import pylaut.utils as utils


class FeatureModel():
    """
    A feature model is the Python object representation of a
    PyLaut feature set. This class performs matching of IPA
    symbols to features and the other way around, as well as
    taking care of background file reading operations for loading
    feature sets.
    """

    _TRUE_FEATURE = "+"
    _FALSE_FEATURE = "-"
    _NULL_FEATURE = "0"
    _possible_feature_values = [_TRUE_FEATURE, _FALSE_FEATURE, _NULL_FEATURE]
    # the longest distance between features that get_ipa_from_features will
    # regard
    _IGNORE_DISTANCE_GREATER_THAN = 5

    JSON_OBJECT_NAME = "featuremodel"
    JSON_VERSION_NO = "pre-alpha-1"

    @staticmethod
    def jdefault(o):
        if isinstance(o, set):
            return list(o)

    def __init__(self, feature_set_file_name, feature_set_path=None):

        # stores whether the feature set defines an IPA lookup table
        self._feature_set_ipa_lookup = False

        self._feature_set_file_name = feature_set_file_name
        self._feature_set_path = feature_set_path

        # self.features is a canonical order for features
        self.features = list()
        self._ipa_dict = dict()
        self._ipa_diacritics = dict()
        self._config = dict()

        self.load_feature_set()

    def _load_feature_set_file(self, fname: str,
                               dir_path: Optional[str]) -> str:
        """
        Helper function to load a feature set from disk.
        May be called with just a name, in which case it will attempt to load
        the feature set from package data. Alternatively, if a directory path
        is passed, the feature set file will be loaded from that directory.

        :param str fname: The file to load.
        :param Optional[str] dir_path: An optional directory to load from.
        :returns: The contents of the file.
        :return-type: str
        """
        if not dir_path:
            try:
                return pkgutil.get_data('pylaut',
                                        f'data/{fname}').decode('utf-8')
            except IOError as ie:
                raise f"""Couldn't load feature set '{fname}' from package!
                Did you forget to specify a file path?""" from ie
        else:
            try:
                path = pathlib.Path(dir_path) / fname
                resolved_path = path.resolve()
                with resolved_path.open('r', encoding='utf-8') as inf:
                    ret = inf.read()
                return ret
            except IOError as ie:
                raise f"""Couldn't load feature set '{resolved_path}'.
                Please double-check the file name and path!""" from ie

    def _load_feature_set_ipa_tables(
            self, feature_set: Dict[str, Any],
            dir_path: Optional[str]) -> Optional[Tuple[str, str]]:
        """
        Helper method to load IPA lookup tables from disk. Takes
        the already read lines of a featureset file and checks if
        the featureset defines IPA lookup, then, if this is the case,
        reads the appropriate files and returns the contents.

        :param List[str] feature_set_raw: A feature set file, as lines.
        :param Optional[str] dir_path: An optional directory to load from.
        :returns: None if the feature set does not have a lookup table.
                  A tuple with the contents of the IPA symbol file first
                  and those of the diacritic file second, otherwise.
        :return-type: Optional[(str, str)]
        """

        if 'segments' not in feature_set or 'diacritics' not in feature_set:
            raise ValueError(
                'Feature set file does not define lookup headers!')
        if not feature_set['segments']:
            # The feature set does not define IPA lookup
            return None

        ipa_file_name = feature_set['segments']
        ipa_dcs_file_name = feature_set['diacritics']

        if not dir_path:
            try:
                ipa_file = pkgutil.get_data(
                    'pylaut', f'data/{ipa_file_name}').decode('utf-8')
                if ipa_dcs_file_name:
                    ipa_dcs_file = pkgutil.get_data(
                        'pylaut', f'data/{ipa_dcs_file_name}').decode('utf-8')
                else:
                    ipa_dcs_file = None
            except IOError as ie:
                raise "Invalid IPA lookup file!" from ie

        else:
            try:
                ipa_file_path = pathlib.Path(dir_path) / ipa_file_name
                with ipa_file_path.open('r', encoding='utf-8') as ipaf:
                    ipa_file = ipaf.read()
                if ipa_dcs_file_name:
                    ipa_dcs_file_path = pathlib.Path(
                        dir_path) / ipa_dcs_file_name
                    with ipa_dcs_file_path.open(
                            'r', encoding='utf-8') as ipadcf:
                        ipa_dcs_file = ipadcf.read()
                else:
                    ipa_dcs_file = None
            except IOError as ie:
                raise "Invalid IPA lookup file!" from ie

        return ipa_file, ipa_dcs_file

    def load_feature_set(self) -> None:
        """
        Loads a feature set from disk, parses its files and
        stores the relevant properties in the FeatureModel object.
        """

        feature_set_raw = self._load_feature_set_file(
            self._feature_set_file_name, self._feature_set_path)
        # feature_set_lines = feature_set_raw.split('\n')

        feature_set = yaml.load(feature_set_raw, Loader=Loader)

        ipa_files_raw = self._load_feature_set_ipa_tables(
            feature_set, self._feature_set_path)
        if ipa_files_raw:
            self._feature_set_ipa_lookup = True

        # assign properties
        self.features = feature_set['features']

        # does the feature set specify ipa lookup?
        if self._feature_set_ipa_lookup and not self._ipa_dict:
            feature_set_ipa_vals_raw = ipa_files_raw[0].split('\n')

            for line in feature_set_ipa_vals_raw[1:]:
                if line:
                    feature_set_ipa_val = line.split()
                    feats = [
                        features for features in
                        feature_set_ipa_val[1:len(feature_set_ipa_val)]
                    ]
                    self._ipa_dict[feature_set_ipa_val[0]] = feats

            if not self._ipa_diacritics:
                feature_set_ipa_dcs_raw = ipa_files_raw[1]
                if feature_set_ipa_dcs_raw:
                    feature_set_ipa_dcs_raw = feature_set_ipa_dcs_raw.split(
                        '\n')
                    for line in feature_set_ipa_dcs_raw[1:]:
                        if line:
                            feature_set_ipa_dc = line.split()
                            # this is a more natural notation for a feature
                            # also the notation that get_ipa_from_features uses
                            self._ipa_diacritics[
                                feature_set_ipa_dc[0]] = frozenset(
                                    feature_set_ipa_dc[1:])

    def get_features_from_ipa(self, ipa_str: str) -> List[str]:
        """
        Takes Unicode IPA symbol (optionally with diacritics) and returns the
        feature-set represented by this IPA. May throw a KeyError if the
        feature set has no value for a certain symbol.

        :param str ipa_str: The IPA string to look up.
        :returns: The features as a list of feature values in canonical order.
        :return-type: List[str]
        """
        ipa_char_features = self._ipa_dict[ipa_str[0]].copy()

        if len(ipa_str) > 1:
            for char in ipa_str[1:]:
                try:
                    dc_feats = self._ipa_diacritics[char]
                    for feat in dc_feats:
                        dc_val = feat[0]
                        if dc_val == self._NULL_FEATURE:
                            continue
                        dc_fname = feat[1:]
                        idx = self.features.index(dc_fname)
                        ipa_char_features[idx] = dc_val
                except KeyError:
                    raise KeyError(" {} not found in IPA lookup.".format(char))
        return ipa_char_features

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
                distant_symbols += [our + self.features[i]]

        return (distant_symbols, len(distant_symbols))

    def is_good_feature(self, feature):
        if feature in self.features:
            return True
        else:
            return False

    def is_good_ipa(self, feature_list):
        """
        Returns an IPA symbol if the Phone fits an IPA symbol in the feature-
        set used, requiring no diacritics, and None otherwise.
        """
        matching_symbols = list()
        for ipa_char in self._ipa_dict:
            if self._ipa_dict[ipa_char] == feature_list:
                matching_symbols += [ipa_char]

        if len(matching_symbols) > 1:
            raise Exception("Multiple symbols match Phone: check feature set "
                            "for non-contrasting symbols.")
        elif len(matching_symbols) < 1:
            return None
        else:
            return matching_symbols[0]

    def get_ipa_from_features(self, feature_list):
        """
        Returns a string giving an IPA representation of the Phone.
        """
        # check to see if the phone has a good IPA representation first
        symbol = self.is_good_ipa(feature_list)
        # if it does, return it
        if symbol:
            return symbol
        # otherwise proceed: we must identify a similar base IPA glyph and then
        # add diacritics
        # get feature list to compare to Phone._ipa_dict
        # stores (features differing, number of different features
        # = hamming dist)
        # indexed by ipa char
        hamming_dict = dict()

        for ipa_char in self._ipa_dict:
            ipa_feature_list = self._ipa_dict[ipa_char]
            diffs, hamming_dist = self.feature_hamming(feature_list,
                                                       ipa_feature_list)
            # ignore ipa symbols infeasibly far -- they are unlikely to make
            # good representations
            if hamming_dist > self._IGNORE_DISTANCE_GREATER_THAN:
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

        # look to see which of these can have diacritics added, work out which

        # reverse Phone._ipa_diacritics so we can look up diacritics
        # from the feature
        reverse_diacritics = {a: b for b, a in self._ipa_diacritics.items()}

        # this will hold our final candidates
        valid = list()

        # go through our first-round candidates
        for distance in hamming_dict_collected:
            for candidate_base, diffs in hamming_dict_collected[distance]:
                # every feature in the first-round candidates is checked to see
                # if there is a diacritic, if there is we note what the
                # diacritic is, otherwise we leave an ominous blank

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
        #       if it is unique, use that, otherwise I D K
        # for now we pick the first one, if there are any...
        if len(valid) < 1:
            raise Exception("No IPA representation found for Phone!")
        else:
            final_choice = valid[0]

        final_glyph = final_choice[0] + "".join(final_choice[1])
        return final_glyph

    def to_json(self):
        """
        Returns a JSON representation of the FeatureModel
        """
        return json.dumps(self.__dict__, default=self.jdefault)

    def from_json(self, json_fm):
        """
        Reinitialise from JSON representation of the FeatureModel
        """
        pre_fm = json.loads(json_fm)

        if "JSON_OBJECT_NAME" not in pre_fm:
            raise Exception("JSON input malformed: no JSON_OBJECT_NAME given.")
        if pre_fm["JSON_OBJECT_NAME"] != self.JSON_OBJECT_NAME:
            raise Exception("JSON type error: was "
                            "given {}, should be {}.".format(
                                pre_fm["JSON_OBJECT_NAME"],
                                self.JSON_OBJECT_NAME))
        if pre_fm["JSON_VERSION_NO"] != self.JSON_VERSION_NO:
            raise Exception("JSON version error: was "
                            "given {}, should be {}.".format(
                                pre_fm["JSON_VERSION_NO"],
                                self.JSON_VERSION_NO))

        self.__dict__ = pre_fm
