#!/usr/bin/python
# -*- coding: utf-8 -*-

symbol_table = {"/":self.mk_conditional(),
                "_":self.mk_environment(),
                "->":self.mk_change(),
                "[":self.mk_feature_list(),
                "+":self.mk_true_feature(),
                "-":self.mk_false_feature()}
