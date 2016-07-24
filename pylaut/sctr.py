#!/usr/bin/python
# -*- coding: utf-8 -*-

import scparse as sp
import change

class translator:
    
    def __init__(self, tree):
        self.stack = []
        self.nodestack = []
        self.tree = tree
        self.symbol_table = {"/":self.mk_conditional,
                             "_":self.mk_environment,
                             "->":self.mk_change,
                             "[":self.mk_feature_list,
                             "+":self.mk_feature_true,
                             "-":self.mk_feature_false}
        #self.change = change.UnconditionalShift()

    def translate(self, tree):
        print(tree)
        for k in range(len(tree)):
            if isinstance(tree[k], str):
                try:
                    self.symbol_table[tree[k]](tree[k+1:])
                except KeyError:
                    return tree[0];
                break

    def mk_conditional(self, arg_v):
        conditional = arg_v[0]
        result = arg_v[1]
        cd_tr = self.translate(conditional)
        self.translate(result)
        #self.change.condition = cd_tr
        print(cd_tr)

    def mk_environment(self, arg_v):
        ante = arg_v[0] 
        post = arg_v[1]
        ante_tr = self.translate(ante)
        post_tr = self.translate(post)
        out = "before %s, after %s".format(ante_tr, post_tr)
        
    def mk_change(self, arg_v):
        origin = arg_v[0]
        target = arg_v[1]
        o_tr = self.translate(origin)
        t_tr = self.translate(target)
        out = "change %s to %s".format(o_tr, t_tr)
        return out

    def mk_feature_list(self, arg_v):
        feature_list = []
        feature_list.append(self.translate(arg) for arg in arg_v)
        return feature_list

    def mk_feature_true(self, arg_v):
        return "+" + self.translate(arg_v[0])

    def mk_feature_false(self, arg_v):
        return "-" + self.translate(arg_v[0])

#DEBUG

stree = sp.parse("[+stop, -voice] -> [+stop, +voice] / V_V")
tr = translator(stree)
tr.translate(tr.tree)

#tr = translator(stree, stable)
