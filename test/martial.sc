% Changes from Shapshirruckish to Proto-Martial

GROUP
META Name "Zerger's Sibilant Rules"
META Description "Zerger's Sibilant Rules (Z.S.R.) are a set of sound laws,
                  all of which take place in or around sibilants, and are common to all the Martial languages.
                  They essentially set up the basis for Martial syllable structure,
                  vowel length and nasal consonants. They are divided into five phases."
META Date 500
BEGIN

  CHANGE
  META Name "Zergerian Muogenesis"
  META Description "Prior to the Z.M. phase (q.v.), /p/ acquires a distinctly nasal character
                    in this particular environment."
  BEGIN
    /p/ -> /m/ | _[+sibilant]
  END

  CHANGE
  META Name "Zergerian Metathesis"
  META Description "This breaks up the most common clusters in Shapshiruckish, p + sibilant.
                    Z.M. along with Z.L. (v.i.) only act on s and ś, suggesting that there
                    is something unusual about ß. Since in Religio-Marine, ß becomes a 'long s',
                    this feature is described as 'length'.

                    This is the beginning of a more general suite of rules which break Proto-Martial
                    into a language with strict (C)V syllable structure. For now, it makes more clusters!"
  BEGIN
    Metathesis([+sibilant -voice],[-consonantal])
    Resyllabify()
  END

  CHANGE
  META Name "Zergerian Lengthening"
  META Description "The limited scope of this rule allows for the reconstruction of ß, bearing in mind Z.Sh. (q.v.)"
  BEGIN
    Lengthen([-consonantal]) | _[+sibilant -voice]
  END

  CHANGE
  META Name "Zergerian Nuogenesis"
  META Description "This is a temporary step backwards in the conspiracy towards (C)V syllable structure"
  BEGIN
    /ʃ/ -> /sn/
  END

  CHANGE
  META Name "Zergerian Shortening"
  META Description "Where Z.L. acts on vowels, Z.Sh. is really just a merger of 'long' ß and s."
  BEGIN
    /z/ -> /s/
  END
END

CHANGE
META Name "Numerical Resolution"
META Description "The numerical phonemes (Ⅰ, Ⅱ and Ⅲ) can be reconstructed more clearly in Proto-Martial.
                  -- Ⅰ causes following vowels to lengthen, or at the end of words, the vowel preceding it.
                  It is lost, unless it is syllabic, when it goes to ā, where it undergoes later harmonisation.
                  -- Ⅱ goes regularly to f or v.
                  -- Ⅲ goes to z.
                 "
META Date 550
BEGIN
  Lengthen([-consonantal]) |  /h/_
                           | _/h/#
  
  /h/ => /aː/ | [+consonantal]_[+consonantal]
      => /aː/ | [+consonantal]_#
      => /0/  
  
  IntervocalVoicing(/f/)
  
  /θ/ -> /z/
END

CHANGE
META Name "Blowatz' Law"
META Date 600
BEGIN
  Merge({/d/,/t/},/l/) | _[-consonantal +round, back]
END

GROUP
META Name "Martial Harmonization"
META Description "A complex reorganisation of the vowel system and the addition of a lot of epentheses
                  result in Martial openness/rounding vowel harmony. An interesting result of this is
                  that the many Shapshiruckish paradigms with -u- and -a- suffixes alternate forms
                  depending on the root.

                  The Martial vowel system settles into an eight-vowel system, with a five-way distinction
                  in long vowels and a three-way distinction in long vowels."
META Date 650
BEGIN

  CHANGE
  META Name "Martial Purification"
  META Description "the dipthongs purify, where they have not already been broken up through Z.S.R.
                    and become long vowels"
  BEGIN
    {/ui/, /ai/, /iə/} -> {/uː/, /eː/, /iː/}
  END

  CHANGE
  META Name "Martial Short Resolution"
  META Description "Short a i and u continue through much as they are.
                    The resolution of e, w and o depends on their environment."
  BEGIN
     
    {/ə/,/ɯ/,/ɒ/} => {/eː/, /ɯː/, /oː/} | in Syllable[0]
                  => {/a/,  /u/,  /a/}  | if Syllable[0].nucleus is [+round]
                  => {/i/,  /i/,  /a/}
    
    /ə/ -> /e/
    /əː/ -> /eː/
    
    Resyllabify()
  END

  CHANGE
  META Name "Martial Epenthesis"
  META Description "Vowels are epenthesized depending on the initial vowel of the word."
  BEGIN
    Epenthesis([+consonantal], /a/) & if Syllable[0].nucleus.quality is /a/
                                    | _[+consonantal]
                                    | _#
    Resyllabify()
    
    Epenthesis([+consonantal], /a/) & if Syllable[0].nucleus.quality is /e/
                                    | _[+consonantal]
                                    | _#
    Resyllabify()
                                  
    Epenthesis([+consonantal], /a/) & if Syllable[0].nucleus.quality is /o/
                                    | _[+consonantal]
                                    | _#
    Resyllabify()
    
    Epenthesis([+consonantal], /i/) & if Syllable[0].nucleus.quality is /i/
                                    | _[+consonantal]
                                    | _#
    Resyllabify()
    
    Epenthesis([+consonantal], /i/) & if Syllable[0].nucleus.quality is /ɯ/
                                    | _[+consonantal]
                                    | _#
    Resyllabify()
    
    Epenthesis([+consonantal], /u/) & if Syllable[0].nucleus.quality is /u/
                                    | _[+consonantal]
                                    | _#
    Resyllabify()
  END

  CHANGE
  META Name "Mitwitz' Law"
  BEGIN
    /ɯː/ -> /iː/
  END

  CHANGE
  META Name "Non-Zergerian Deletion"
  META Description "Between vowels of same quality, but not necessarily same length,
                    s disappears, and the two-vowel cluster goes to a single long vowel."
  BEGIN
    /s/ -> /0/ & [-consonantal]_[-consonantal]
               & if Phone[@-1].quality = Phone[@1].quality
    
    [-consonantal] -> /0/ & [-consonantal]_
                          & if Phone[@-1].quality = Phone[@0].quality
  END

  CHANGE
  META Name "Hiatus Resolution"
  META Description "Where two long vowels are next to each other, the second is lost."
  BEGIN
    [-consonantal +long] -> /0/ | [-consonantal +long]_

    Resyllabify()
  END
END