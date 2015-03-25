#!/usr/bin/python
# -*- coding: utf-8 -*-

import scparse as sp
import change
from translation_functions import symbol_table

class translator:
    
    def __init__(self, tree, s_table):
        self.stack = []
        self.tree = tree.reverse()
        self.symbol_table = s_table
        self.change = ConditionalShift()

    def read_tree(self):
        self.tree.reverse()
        for node in tree:
            self.stack.append(node)

    def translate(self, node = False):
        if not node:
            node = self.stack.pop()
        if not isinstance(node, list):
            try:
                self.symbol_table[node]
            except KeyError:
                return node

    def mk_conditional(self):
        conditional = self.stack.pop()
        result = self.stack.pop()
        cd_tr = self.translate(conditional)
        self.translate(result)
        self.change.condition = cd_tr

    def mk_change(self):
        origin = self.stack.pop()
        target = self.stack.pop()



        

#DEBUG

stree = sp.parse("[+stop, -voice] -> [+stop, +voice] / V_V")
tr = translator(stree, symbol_table)
tr.read_tree()
tr.translate()

#tr = translator(stree, stable)
