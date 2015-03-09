#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

def lex(chars, token_exprs, debug=0):
    pos = 0
    tokens = []
    while pos < len(chars):
        match = None
        for token_expr in token_exprs:
            pattern, tag = token_expr
            regex = re.compile(pattern)
            match = regex.match(chars, pos)
            if match: 
                text = match.group(0)
                if tag:
                    token = (text, tag)
                    tokens.append(token)
                    break
            if not match:
                raise Exception("Syntax Error: %s is not a legal expression\n"
            else:
                pos = match.end(0)
        return tokens


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
    return lex(chars, token_exprs)

#DEBUG
#characters = "a->b"
#tokens = sclex(characters)
#for token in tokens:
#    print(token)
