#!/usr/bin/python
# -*- coding: utf-8 -*-

#Code based substantially off work by Jay Conrod at jayconrod.com

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
            raise Exception("Syntax Error: %s is not a legal expression\n" % chars[pos])
        else:
            pos = match.end(0)
    return tokens

