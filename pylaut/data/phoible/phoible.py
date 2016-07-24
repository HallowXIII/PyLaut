import csv
from pprint import pprint

#http://stackoverflow.com/posts/11158224/revisions
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

import phonology

def get_phonology(lang,dataset):

    phonemes = dict()
    
    with open("phoible-phonemes.tsv","r") as phoible_file:
        phoible_file = csv.reader(phoible_file, delimiter = "\t")
        
        for row in phoible_file:
            if row[3].title() == lang.title():
                if row[8] != "tones":
                    if row[1] not in phonemes:
                        phonemes[row[1]] = [row[7]]
                    else:
                        phonemes[row[1]] += [row[7]]

    if dataset not in phonemes:
        raise Exception("{} not present in {}, options: {}".format(lang,dataset," ".join(phonemes.keys())))

    return phonemes[dataset]

ph = phonology.Phonology(get_phonology("Malay","SPA"))

print(ph.get_vowels())
