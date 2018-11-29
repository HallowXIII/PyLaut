#ZSR

/p/ -> /m/ | _[+sibilant]

Metathesis([+sibilant -voice],[-consonantal])

Resyllabify()

Lengthen([-consonantal]) | _[+sibilant -voice]

/ʃ/ -> /sn/

/z/ -> /s/ 

#NR

Lengthen([-consonantal]) |  /h/_
                         | _/h/#

/h/ => /aː/ | [+consonantal]_[+consonantal]
    => /aː/ | [+consonantal]_#
    => /0/  

IntervocalVoicing(/f/)

/θ/ -> /z/

#BL
Merge({/d/,/t/},/l/) | _[-consonantal, rounded, back]

#MP

{/ui/, /ai/, /iə/} -> {/uː/, /eː/, /iː/}

#MSR
{/ə/,/ɯ/,/ɒ/} => {/eː/, /ɯː/, /oː/} | in Syllable[0]
              => {/a/,  /u/,  /a/}  | if Syllable[0].nucleus is [+round]
              => {/i/,  /i/,  /a/}

/ə/ -> /e/
/əː/ -> /eː/

Resyllabify()

#ME
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

#ML
/ɯː/ -> /iː/

#NZD
/s/ -> /0/ & [-consonantal]_[-consonantal]
           & if Phone[@-1].quality = Phone[@1].quality

[-consonantal] -> /0/ & [-consonantal]_
                      & if Phone[@-1].quality = Phone[@0].quality

#HR
[-consonantal +long] -> /0/ | [-consonantal +long]_

Resyllabify()
