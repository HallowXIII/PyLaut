import word, phonology, family

class Condition(object):
    def __init__(self):
        pass

class Change(object):
    def __init__(self):
        self.domain = []
        self.codomain = []
        self.changes = {}
        self.condition = []

    def add_to_domain(self,phoneme_list):
        if type(phoneme_list) == set:
            phoneme_list = list(phoneme_list)
        self.domain.extend(phoneme_list)
    def add_feature_changes(self,feature_dict):
        for feature, value in feature_dict.items():
            self.changes[feature] = value
            
    def apply(self,word_obj):
        return word_obj

class UnconditionalShift(Change):
    def __init__(self):
        super().__init__()
        self.condition = True

    def compute_codomain(self):
        self.codomain = []
        print(self.domain)
        for feature, value in self.changes.items():
            for phoneme in self.domain:
                #this works b/c it is a simple 1-to-1 mapping with no branching
                #outcomes from conditions
                if value == "+":
                    newphoneme = phoneme.copy()
                    newphoneme.set_features_true(feature)
                elif value == "-":
                    newphoneme = phoneme.copy()
                    newphoneme.set_features_false(feature)
                elif value == "0":
                    newphoneme = phoneme.copy()
                    newphoneme.set_features_null(feature)
                newphoneme.set_symbol_from_features()
                self.codomain += [newphoneme]       

    def apply(self,word_obj,word_factory):
        newword = word_factory.make_word(word_obj.__repr__()[1:-1])
        for i, o in zip(self.domain,self.codomain):
            for syllable in newword.phonemes:
                for j, phoneme in enumerate(syllable):
                    if phoneme == i:
                        syllable[j] = o
        return newword

class ConditionalShift(UnconditionalShift):
    def __init__(self, condition):
        super().__init__()
        self.condition = condition

#    def apply(self,word_obj,word_factory):
#        newword = word_factory.make_word(word_obj.__repr__()[1:-1])
#        for i, o in zip(self.domain,self.codomain):
#            for syllable in newword.phonemes:
#                for j, phoneme in enumerate(syllable):
#                    if phoneme == i and self.condition[phoneme] == True:
#                        syllable[j] = o 
#        return newword                  
                                         
class ChangeFactory(object):             
    def __init__(self):                  
        pass                             
                                         
if __name__ == "__main__":               

    shapfam = family.FamilyFactory("everywhere.fam").get()
    shap = shapfam.protolang
    sample = shap.lexicon.get_random_entry_with_segment("p") 

    lol = {"voice":"-",
           "continuant":"-"
          }
    unvoiced_stops = shap.lexicon.phonology.get_phonemes_with_features(lol)

    lenite = UnconditionalShift()
    lenite.add_to_domain(unvoiced_stops)

    change = {"voice":"+"}
    lenite.add_feature_changes(change)
    lenite.compute_codomain()
    print(lenite.codomain)

    shapfac = word.WordFactory(shap.lexicon.phonology)
    sample2 = lenite.apply(sample,shapfac)

    print(sample,sample2)
