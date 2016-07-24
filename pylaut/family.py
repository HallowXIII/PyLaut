from pprint import pprint
import json
import lexicon

class Family(object):
    def __init__(self):
        self.name = ""
        self.protolang = None
        self.calendar_signed = True
        self.calendar_has_zero = True
        self.calendar = [" BE"," E"]
    
    def set_name(self,name):
        self.name = name
        
    def set_proto_language(self,lang):
        self.protolang = lang

    def set_calendar_gregorian(self):
        self.calendar_signed = True
        self.calendar_has_zero = False
        self.calendar = ["BC","AD"]
    def set_calendar_numerical(self):
        self.calendar_signed = False
        self.calendar_has_zero = True
        self.calendar = ["",""]
        
    def add_descendant(self, new_lang,parent_lang = "root"):
        if parent_lang == "root":
            parent_lang = self.protolang
        parent_lang.add_descendant(new_lang)
    
    def get_year_from_calendar(self,date):
        symbol = ""
        if not self.calendar_signed:
            symbol = self.calendar[1]
        else:
            if date < 0:
                symbol = self.calendar[0]
                date = -date
            elif date >= 0:
                if not self.calendar_has_zero:
                    date = date + 1
                symbol = self.calendar[1]
        return ("{} {}".format(date,symbol))
                
        
    def print_langs(self):
        print("{} ({})".format(self.protolang.name, self.get_year_from_calendar(self.protolang.date)))
        for langname, lang in self.protolang.descendants.items():
            print("     {} ({})".format(langname, self.get_year_from_calendar(lang.date)))
            for lang2name, lang2 in lang.descendants.items():
                print("        {} ({})".format(lang2name, self.get_year_from_calendar(lang2.date)))
            
class Language(object):
    def __init__(self):
        self.name = None
        self.lexicon = None
        self.lexicondelta = None
        self.date = None
        self.descendants = dict()
        
    def set_name(self,name):
        self.name =  name

    def set_lexicon(self,lex_obj):
        self.lexicon = lex_obj
        
    def set_date(self,date):
        self.date = date
    
    def add_descendant(self,lang):
        self.descendants[lang.name] = lang
        
class ProtoLanguage(Language):
    pass
    
def dict_insert_or_append(adict,key,val):
    """Insert a value in dict at key if one does not exist
    Otherwise, convert value to list and append
    """
    if key in adict:
        if type(adict[key]) != list:
            adict[key] = [adict[key]]
        adict[key].append(val)
    else:
        adict[key] = val

def ttree_to_json(ttree,level=0):
    result = {}
    for i in range(0,len(ttree)):
        cn = ttree[i]
        try:
            nn  = ttree[i+1]
        except:
            nn = {'level':-1}

        # Edge cases
        if cn['level']>level:
            continue
        if cn['level']<level:
            return result

        # Recursion
        if nn['level']==level:
            dict_insert_or_append(result,cn['name'],cn['value'])
        elif nn['level']>level:
            rr = ttree_to_json(ttree[i+1:], level=nn['level'])
            dict_insert_or_append(result,cn['name'],rr)
        else:
            dict_insert_or_append(result,cn['name'],cn['value'])
            return result
        return result
        
class FamilyFactory(object):

    def __init__(self,file_name):
        self.lexpath = "shap/Everywhere/"
        self.file_name = file_name
            
    def get(self):
                        
        def_file = open(self.lexpath + self.file_name,"r")
        b = json.load(def_file)
        
        proto_lang = ProtoLanguage()
        proto_lang.set_name(b["ProtoLanguage"])
        proto_lang.set_date(b["ProtoDate"])
        proto_lexicon = lexicon.Lexicon()
        proto_lexicon.from_file(open(self.lexpath + b["ProtoLexicon"],"r"))
        proto_lang.set_lexicon(proto_lexicon)

        fam = Family()
        fam.set_name(b["Name"])
        fam.set_proto_language(proto_lang)
        
        for lang in b["Languages"]:
            l = Language()
            l.set_name(lang["Name"])
            l.set_date(lang["Date"])
            fam.add_descendant(l)
            if lang["Languages"]:
                for lang2 in lang["Languages"]:
                    l2 = Language()
                    l2.set_name(lang2["Name"])
                    l2.set_date(lang2["Date"])
                    fam.add_descendant(l2,l)

        return fam        
        


a = FamilyFactory("everywhere.fam").get()

        
