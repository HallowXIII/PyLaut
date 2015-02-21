import word, phonology, family

class Change(object):
    def __init__(self):
        pass
    
    def apply(self,word_obj):
        return word_obj

class UnconditionalShift(Change):
    def __init__(self):
        self.domain = []
        self.codomain = []
        self.changes = {}
        self.condition = True
        
    def add_to_domain(self,phoneme_list):
        if type(phoneme_list) == set:
            phoneme_list = list(phoneme_list)
        self.domain.extend(phoneme_list)
        
    def add_feature_changes(self,feature_dict):
        for feature, value in feature_dict.items():
            self.changes[feature] = value
    
    def compute_codomain(self):
        self.codomain = []
        print(self.domain)
        for feature, value in self.changes.items():
            for phoneme in self.domain:
                if value == "+":
                    newphoneme = phoneme
                    print(feature)
                    newphoneme.set_features_true(feature)
                elif value == "-":
                    newphoneme = phoneme
                    newphoneme.set_features_false(feature)
                elif value == "0":
                    newphoneme = phoneme
                    newphoneme.set_features_null(feature)
                newphoneme.set_symbol_from_features()
                self.codomain += [newphoneme]

    def apply(self,word_obj):
        newword = word_obj
        #PICK UP
        
shapfam = family.FamilyFactory("everywhere.fam").get()
shap = shapfam.protolang
sample = shap.lexicon.get_random_entry_with_segment("pi") 
print(sample)

lol = {"voice":"-",
       "consonantal":"+",
       "continuant":"-"}
unvoiced_stops = shap.lexicon.phonology.get_phonemes_with_features(lol)

lenite = UnconditionalShift()
lenite.add_to_domain(unvoiced_stops)

change = {"voice":"+"}
lenite.add_feature_changes(change)
lenite.compute_codomain()
print(lenite.codomain)

sample2 = lenite.apply(sample)

print(sample,sample2)
