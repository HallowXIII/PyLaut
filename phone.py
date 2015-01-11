from pprint import pprint

class Phone(object):
    """
    Phones are the atomic unit of PyLaut. They are somewhere between acoustic
    phones and phonemes.
    
    They are a collection [dictionary + canonical order] of phonological features
    with extra structure to make manipulating them easier.
    """
    #the values features can take.
    _TRUE_FEATURE = "+"
    _FALSE_FEATURE = "-"
    _NULL_FEATURE = "0"
    _possible_feature_values = [_TRUE_FEATURE, _FALSE_FEATURE, _NULL_FEATURE]
    
    #stores whether the feature set defines an IPA lookup table
    _FEATURE_SET_IPA_LOOKUP = False
    _feature_set_ipa_dict = dict()    
    
    #the longest distance between features that get_ipa_from_features will regard
    _IGNORE_DISTANCE_GREATER_THAN = 5
            
            
    def __init__(self):

        self.feature_set_name = None

        #the features of the Phone
        self.features = dict()
        #self.feature_set is a canonical order for features
        self.feature_set = list()
        
        #representation of the Phone
        self.symbol = "0"
    
    
    def __repr__(self):
        """
        Actually there are many choices for the default representation, but for
        now it uses print_feature_list"
        """
        return self.print_feature_list()
    
        
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
                
        return " ".join(output)
    
    
    def load_set_feature_set(self,feature_set_file_name):
        """
        Loads a feature set from file, sets the Phone's feature set to it and 
        reinits self.features /!\ clearing any existing features /!\
        
        A feature set file is a plain text file, with the name of the feature set
        on the first line, with features given in []s each on its separate line
        """
        feature_set_raw = open(feature_set_file_name,"r").read().splitlines()
        feature_set_name = feature_set_raw[0]
        if feature_set_raw[1]:
            if feature_set_raw[1] != "0":
                Phone._FEATURE_SET_IPA_LOOKUP = True
                feature_set_ipa_filename = feature_set_raw[1]
        feature_set = [line for line in feature_set_raw if line and 
                       line[0] == "[" and line[-1] == "]" ]
        feature_set = [line[1:-1] for line in feature_set]
        
        #assign properties
        self.feature_set_name = feature_set_name
        self.feature_set = feature_set
        self.features = {x: None for x in self.feature_set}
        #does the feature set specify ipa lookup?
        if Phone._FEATURE_SET_IPA_LOOKUP and not Phone._feature_set_ipa_dict:
            try:
                feature_set_ipa_vals_raw = open(feature_set_ipa_filename,"r").read().splitlines()
            except IOError:
                raise Exception("Invalid IPA lookup file!")
        for line in feature_set_ipa_vals_raw[1:]:
            if line:
                feature_set_ipa_val = line.split()
                Phone._feature_set_ipa_dict[feature_set_ipa_val[0]] = [features for features in feature_set_ipa_val[1:len(feature_set_ipa_val)]]


    def clear_features(self):
        """
        Clears the entries of self.features.
        """
        self.features = {x: None for x in self.feature_set}


    def set_feature(self,feature_name,feature_value):
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
                                "Phone".format(feature_value) )
            else:
                #do it
                self.features[feature_name] = feature_value


    def set_features_bool(self,feature_names,hey_boo):
        """
        Used by set_features_true/false/null
        
        hey_boo is the object that the feature is set to
        
        """
        #in case we are passed a string and not a list, so the loop can iterate
        #through it properly
        if type(feature_names) == str:
            feature_names = [feature_names]
        
        for feature_name in feature_names:
            self.set_feature(feature_name,hey_boo)

            
    def set_features_true(self,feature_names):
        """
        Sets the feature_name of the Phone to be true/+
        """
        self.set_features_bool(feature_names,Phone._TRUE_FEATURE)

    
    def set_features_false(self,feature_names):
        """
        Sets the feature_name of the Phone to be false/-
        """
        self.set_features_bool(feature_names,Phone._FALSE_FEATURE)

    
    def set_features_null(self,feature_names):
        """
        Sets the feature_name of the Phone to be null/0
        """
        self.set_features_bool(feature_names,Phone._NULL_FEATURE)


    def set_features_from_ipa(self,ipa_char):
        """
        Takes Unicode IPA symbol and automagically assigns appropriate featural 
        values to Phone
        """
        ipa_char_features = Phone._feature_set_ipa_dict[ipa_char]
        
        #clear the features dict to prepare for the IPA data [which should be
        #complete + contain a value for all features]
        self.clear_features()
        
#        #XXX: can u not iterate directly over the feature_set?
#        #     cf. the inverse function of this -P 11/01/2015
#        #XXX: i rewrote it, pls c b-low -P 11/01/2015
#
#        for i in range(len(self.feature_set)):
#            if ipa_char_features[i] == "+":
#                self.set_features_true(self.feature_set[i])
#            elif ipa_char_features[i] == "-":
#                self.set_features_false(self.feature_set[i])
#            else:
#                self.set_features_null(self.feature_set[i])
    
        for ipa_feat, our_feat in zip(ipa_char_features, self.feature_set):
            if ipa_feat == Phone._TRUE_FEATURE:
                self.set_features_true(our_feat)
            elif ipa_feat == Phone._FALSE_FEATURE:
                self.set_features_false(our_feat)
            else:
                self.set_features_null(our_feat)

                
    def feature_hamming(self,feature_list,ipa_feature_list):
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
                distant_symbols += [our+self.feature_set[i]]
                
        return (distant_symbols,len(distant_symbols))


    def get_feature_list(self):
        """
        Returns a list of the values of features from self.features, using the 
        canonical order from self.feature_set.
        """
        feature_list = list()
        for feature in self.feature_set:
            feature_list += [self.features[feature]]
        return feature_list

        
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
        #check to see if the phone has a good IPA representation first
        symbol = self.is_good_ipa()
        #if it does, return it
        if symbol:
            return symbol
        #otherwise proceed: we must identify a similar base IPA glyph and then
        #add diacritics
        else:
            pass
            
        #get feature list to compare to Phone._feature_set_ipa_dict
        our_feature_list = self.get_feature_list()
        #stores (features differing, number of different features = hamming dist)
        #indexed by ipa char
        hamming_dict = dict()

        for ipa_char in Phone._feature_set_ipa_dict:
            ipa_feature_list = Phone._feature_set_ipa_dict[ipa_char] 
            diffs, hamming_dist = self.feature_hamming(our_feature_list,ipa_feature_list)
            #ignore ipa symbols infeasibly far -- they are unlikely to make good
            #representations
            if hamming_dist > Phone._IGNORE_DISTANCE_GREATER_THAN:
                pass
            else:
                hamming_dict[ipa_char] = (diffs, hamming_dist)

        #compile a list from hamming_dict, sorting by hamming_dist
        hamming_list = sorted(hamming_dict.items(),key=lambda x:x[1][1])

        #collect items in hamming_list together into a dictionary
        #index is hamming distance between phone and base ipa chars
        #values are lists of tuples (ipa char, diffs)
        hamming_dict_collected = dict()
        for symbol, (diffs,distance) in hamming_list:
            if distance in hamming_dict_collected:
                hamming_dict_collected[distance] += [(symbol,diffs)]
            else:
                hamming_dict_collected[distance] = [(symbol,diffs)]

        pprint(hamming_dict_collected)
        
        #TODO: go through hamming_dict_collected, deleting diffs which do not
        #have diacritics allowing the change to happen
        
        #TODO: identify the lowest-indexed solutions thus left
        #      if it is unique, use that, otherwise I D K
        
        #TODO: pick out and append the diacritics to the nearest base
        
        #TODO: return it
        return "0"


                    
class MicroPhone(Phone):
    """
    MicroPhones are Phones which use the MICROMONOPHONE feature-set. For further 
    information, please refer to Phone.
    """
    def __init__(self):
        super().__init__()
        self.load_set_feature_set("micromonophone")



class MonoPhone(Phone):
    """
    MonoPhones are Phones which use the MONOPHONE feature-set. For further 
    information, please refer to Phone.
    """
    def __init__(self):
        super().__init__()
        self.load_set_feature_set("monophone")

################################################################################
#DEBUGGING
################################################################################

if __name__ == "__main__":
    lol = MonoPhone()

    lol.set_features_from_ipa("m")
    lol.set_features_false("voice")
    print(lol.is_good_ipa())
    print("Output: ", lol.get_ipa_from_features())

