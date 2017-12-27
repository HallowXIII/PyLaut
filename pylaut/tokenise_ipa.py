from itertools import tee

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)
    
def tokenise_ipa(s):
    """
    Outputs a tuple of tokenised ipa symbols, with diacritics grouped with base 
    glyphs. If the ipa is presented sI'lab.ik.lI, it outputs a tuple of tuples 
    """
    with open("data/monophone_ipa_diacritics","r") as dia_file:
            read_words = [x for x in dia_file.read().splitlines()]
            diacritics = [x.split()[0] for x in read_words]

    syllable_bounds = "'."
    
    s = s.replace("'",".'")
    sl = s.split(".")
    
    tokens = []
    
    for syllable in sl:
        syllable_tokens = []
        if syllable and syllable[0] == "'":
            stress = "'"
            syl = syllable[1:]
        else:
            stress = ""
            syl = syllable
    
        for i, c in enumerate(syl):
            if c in diacritics:
                pass
            elif i < len(syl)-1 and syl[i+1] in diacritics:
                syllable_tokens += [c + syl[i+1]]
            else:
                syllable_tokens += [c]
        
        tokens += [syllable_tokens]
        
        out = tuple([tuple(x) for x in tokens])
        
        if len(out) == 1:
            out = out[0]

    return out
