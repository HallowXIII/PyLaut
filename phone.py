from pprint import pprint

class Phone(object):
    """
    Phones are the atomic unit of PyLaut. They are somewhere between acoustic
    phones and phonemes.
    
    They are a collection [dictionary + canonical order] of phonological features
    with extra structure to make manipulating them easier.
    """
    #the values features can take.
    #maybe we will change this to "+-0" or something, but i am storing it as a
    #class attribute for convenience

    _TRUE_FEATURE = True
    _FALSE_FEATURE = False
    _NULL_FEATURE = None
    _possible_feature_values = [_TRUE_FEATURE, _FALSE_FEATURE, _NULL_FEATURE]
    
    #stores whether the feature set defines an IPA lookup table
    _FEATURE_SET_IPA_LOOKUP = False
    _feature_set_ipa_dict = dict()    
        
    def __init__(self):
        self.feature_set_name = None
        #self.feature_set is a canonical order for features, so features can be
        #set in one go as e.g. "+++--00+-"
        self.feature_set = list()
        self.features = dict()
        #representation of the Phone
        self.symbol = "0"
        
    def __repr__(self):
        """
        Actually there are many choices for the default representation, but for
        now it produces a string "[+feature] [-lol] [+dongs]"
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
        
        #XXX: can u not iterate directly over the feature_set?
        #     cf. the inverse function of this -P 11/01/2015
        for i in range(len(self.feature_set)):
            if ipa_char_features[i] == "+":
                self.set_features_true(self.feature_set[i])
            elif ipa_char_features[i] == "-":
                self.set_features_false(self.feature_set[i])
            else:
                self.set_features_null(self.feature_set[i])

    def i_farted(self):
        """
        for debug purposes, pls dont use and if at all possible, delete
        """
        print(Phone._feature_set_ipa_dict)
    
    def feature_hamming(self,feature_list,ipa_feature_list):
        return sum(our != ipa for our, ipa in zip(feature_list,ipa_feature_list))
        
    def get_ipa_from_features(self):
        pass
        #get feature list to compare to Phone._feature_set_ipa_dict
        our_feature_list = list()
        for feature in self.feature_set:
            if self.features[feature] == Phone._TRUE_FEATURE:
                addend = "+"
            elif self.features[feature] == Phone._FALSE_FEATURE:
                addend = "-"
            else:
                addend = "0"
            our_feature_list += [addend]
        print(our_feature_list)
        
        #contains the matching symbols + hamming distance
        matching_symbols = list()
        #look through Phone._feature_set_ipa_dict to see if it is in as it is
        for segment in Phone._feature_set_ipa_dict:
            if Phone._feature_set_ipa_dict[segment] == our_feature_list:
                matching_symbols += [(segment,0)]
        
        #if we have come up empty, look for Hamming-nearby symbols
        if not matching_symbols:
            #stores the hamming distance between this phone + all ipa chars
            hamming_dict = dict()
            
            for segment in Phone._feature_set_ipa_dict:
                ipa_feature_list = Phone._feature_set_ipa_dict[segment] 
                hamming_dist = self.feature_hamming(our_feature_list,ipa_feature_list)
                hamming_dict[segment] = hamming_dist
            
            #get a list of (symbol, hamming distance tuples)
            hamming_list = sorted(hamming_dict.items(),key=lambda x:x[1])
            
            hamming_dict_collected = dict()
            for symbol, distance in hamming_list:
                if distance in hamming_dict_collected:
                    hamming_dict_collected[distance] += [symbol]
                else:
                    hamming_dict_collected[distance] = [symbol]
                    
            pprint(hamming_dict_collected)
        return matching_symbols
                    
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
    MicroPhones are Phones which use the MONOPHONE feature-set. For further 
    information, please refer to Phone.
    """
    def __init__(self):
        super().__init__()
        self.load_set_feature_set("monophone")
        
lol = MonoPhone()

lol.set_features_from_ipa("m")
lol.set_features_false("voice")

#the raw feature dict, don't do this
print(lol.features)
#lol.__repr__, do do this
print(lol)
#lol.i_farted()
print(lol.get_ipa_from_features())
