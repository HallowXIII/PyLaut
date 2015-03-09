#!/usr/bin/python
# -*- coding: utf-8 -*-

# With thanks to Effbot and Jay Conrod

import sclex
import sys

symbol_table = {}
#This stores all the symbols we know.

class base_symbol:
    #Defines the common behavior of symbols in the parser
    id = None
    value = None
    first = second = third = None

    def nud(self):
        raise SyntaxError("Syntax Error: (%r.)" % self.id)

    def led(self):
        raise SyntaxError("Unknown Operator: (%r.)" % self.id)

    def __repr__(self):
        if self.id == "(literal)":
            return "(%s %s)" % (self.id[1:-1], self.value)
        out = [self.id, self.first, self.second, self.third]
        out = map(str, filter(None, out))
        return "(" + " ".join(out) + ")"

def symbol(id, bp=0):
    #Factory function that generates new symbol classes on the fly. 
    #This makes the parser pretty easily extendable.
    try:
        s = symbol_table[id]
    except KeyError:
        class s(base_symbol):
            pass
        s.__name__ = "symbol-" + id
        s.id = id
        s.lbp = bp
        symbol_table[id] = s
    else:
        s.lbp = max(bp, s.lbp)
    return s

#Next we define the symbol classes. For now there are three: the default symbol that doesn't bind, left-binding operators and the right-binding condition operator.
#TODO: think about the grammar, define the rest of the things we want

def op_binary(id, bp):
    def led(self, left):
        self.first = left
        self.second = expression(bp)
        return self
    symbol(id, bp).led = led

def op_bin_r(id, bp):
    def led(self, left):
        self.first = expression(bp)
        self.second = left
        return self
    symbol(id, bp).led = led

symbol("(literal)").nud = lambda self: self
#Literals are just literals, so they don't bind and return themselves.
symbol("(end)")
#The end operator has bp 0 and so terminates the program.
op_bin_r("/", 10)
op_binary("->", 20)
op_binary("_", 50)
#HACK this should work, but I'm not sure whether implementing "_" this way is pretty

def tokenize(program):
    #This takes calls the lexer and translates its output into things the parser understands.
    for token, tag in sclex.sclex(program):
        if tag == "LIT":
            symbol = symbol_table["(literal)"]
            s = symbol()
            s.value = token
            yield s
        else:
            symbol = symbol_table.get(token)
            if not symbol:
                raise SyntaxError("Unknown Symbol")
            yield symbol()
    symbol = symbol_table["(end)"]
    yield symbol()

def expression(rbp=0):
    #This function advances through the token stream and ends when it encounters an (end) marker.
    global token
    t = token
    token = next()
    left = t.nud()
    while rbp < token.lbp:
        t = token
        token = next()
        left = t.led(left)
    return left

def parse(program):
    #Simple driver function. Basically, this is what's used to call the machinery.
    global token, next
    next = tokenize(program).__next__
    token = next()
    return expression()



print(parse("y -> b / V_V"))
