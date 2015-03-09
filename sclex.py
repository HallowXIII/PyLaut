#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import lexer

#This is basically just a listing of the operators we recognize. 
       
RESERVED = 'RESERVED'
LIT = 'LIT'

token_exprs = [
        (r'[ \\n\\t]+', None),
        (r'/\*[^\\n]*', None),
        (r'->',         RESERVED),
        (r'/',          RESERVED),
        (r'_',          RESERVED),
        (r'=',          RESERVED),
        (r'\(',         RESERVED),
        (r'\)',         RESERVED),
        (r'{',          RESERVED),
        (r'}',          RESERVED),
        (r'!',          RESERVED),
        (r'!=',         RESERVED),
        (r'\?',         RESERVED),
        (r'\[',         RESERVED),
        (r'\]',         RESERVED),
        (r'#',          RESERVED),
        (r'\$',         RESERVED),
        (r'(?!_)[\w+]', LIT)
        ]

#TODO review character set

def sclex(chars):
    return lexer.lex(chars, token_exprs)

#DEBUG
#characters = "a->b"
#tokens = sclex(characters)
#for token in tokens:
#    print(token)
