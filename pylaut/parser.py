from lark import Lark, ParseError, Transformer
from lark.lexer import Token
from pkgutil import get_data
from pylaut.phone import Phone
from pylaut.phonology import Phoneme
from pylaut.word import Syllable
from pylaut.change import Change, This, ChangeGroup
from pylaut.change_functions import replace_phonemes, change_feature
from pylaut.pylautlanglib import make_predicate
import functools as ft
import pdb


def get_parser():
    pllg = Lark(get_data("pylaut", "data/pylautlang.g").decode("utf-8"))
    #                parser = "lalr")
    return pllg


def phoneme_list_from_string(s):
    p = Phoneme()
    ret = []
    curr = []
    for ch in s:
        if curr == []:
            curr.append(ch)
        elif ch in p._feature_set_ipa_diacritics:
            curr.append(ch)
        else:
            try:
                ret.append(Phoneme(curr))
            except KeyError:
                pass
            curr = [ch]
    try:
        ret.append(Phoneme(curr))
    except KeyError:
        pass
    return tuple(ret)


def flatten(lst):
    return [item for sublist in lst for item in sublist]


class PyLautLang(Transformer):
    def __init__(self, funcs={}):
        super().__init__()
        self.funcs = funcs

    def start(self, l):
        nl = [c for c in l if isinstance(c, Change)]
        return nl

    def label(self, args):
        return args[0]

    def labelled(self, args):
        if len(args) == 2:
            change = args[1]
            change.label = args[0]
        else:
            change = args[0]
        return change

    def phoneme(self, l):
        pl = phoneme_list_from_string(l[0])
        return pl

    def phoneme_list(self, l):
        if len(l) == 1:
            return l[0]
        return tuple(l)

    def simple_unconditional(self, args):
        domain = args[0]
        codomain = args[1]
        return replace_phonemes(domain, codomain)

    def multiple_unconditional(self, args):
        return ChangeGroup(
            [replace_phonemes(d, c) for d, c in zip(args[0], args[1])])

    def change_feature(self, args):
        domain, codomain = args
        ch = Change()
        for name, value in codomain:
            ch = ch.do(lambda p: change_feature(p, name, value))
        return ch

    def replace_by_feature(self, args):
        domain, codomain = args
        conditions = []
        for name, value in domain.items():

            def has_feature(p, n=name, v=value):
                return p.feature_is(n, v)

            conditions.append(has_feature)
        ch = Change().do(lambda p: codomain).to(
            This.forall(Phone)(lambda p, c=conditions: all(f(p) for f in c)))
        return ch

    def and_condition(self, args):
        return (True, args[0])

    def or_condition(self, args):
        return (False, args[0])

    def condition_list(self, args):
        and_conditions = []
        or_conditions = []
        for sigil, condition in args:
            if sigil:
                and_conditions.append(condition)
            else:
                or_conditions.append(condition)

        def predicate(td, ac=and_conditions, oc=or_conditions):
            def run_ac():
                for f in ac:
                    if not f(td):
                        return False
                return True

            def run_oc():
                if not oc:
                    return True
                for f in oc:
                    if f(td):
                        return True
                return False

            return run_ac() and run_oc()

        return predicate

    def basic_conditional(self, args):
        base_change = args[0]
        condition = args[1]
        if isinstance(base_change, list):
            new_change = list(map(lambda c: c.when(condition), base_change))
        else:
            new_change = base_change.when(condition)
        return new_change

    def simple_conditional(self, args):
        changes = []
        domain = args[0]
        default = args[-1]
        for (codomain,
             condition) in zip(*[args[1:-2][i::2] for i in range(2)]):
            ch = self.simple_unconditional([domain, codomain]).when(condition)
            changes.append(ch)
        changes.append(self.simple_unconditional([domain, default]))
        return ChangeGroup(changes)

    def multiple_conditional(self, args):
        changes = []
        domain = args[0]
        default = args[-1]
        for (codomain,
             condition) in zip(*[args[1:-2][i::2] for i in range(2)]):
            ch = self.multiple_unconditional([domain,
                                              codomain]).when(condition)
            changes.append(ch)
        changes.append(self.multiple_unconditional([domain, default]))
        return ChangeGroup(changes)

    def change_feature_conditional(self, args):
        changes = []
        domain = args[0]
        default = args[-1]
        for (codomain,
             condition) in zip(*[args[1:-2][i::2] for i in range(2)]):
            changes += self.simple_conditional(
                [self.simple_unconditional([domain, codomain]), condition])
            changes.append(self.simple_unconditional([domain, default]))
        return changes

    def relative_expr(self, args):
        conditions = []
        this = args.index("_")
        for i in range(len(args)):
            pos = i - this
            arg = args[i]
            if isinstance(arg, list):
                arg = arg[0]
            if isinstance(arg, tuple):
                arg = arg[0]
            if isinstance(arg, str):
                if arg == "#":
                    relpos = -pos
                    conditions.append(This.is_at_index(Phone, relpos))
                elif arg == "_":
                    continue
                else:
                    for p in arg:
                        conditions.append(
                            This.at(Phone, pos, lambda q, p=p: q.is_symbol(p)))
            elif isinstance(arg, dict):
                for k, v in arg.items():
                    conditions.append(
                        This.at(
                            Phone, pos,
                            lambda p, k=k, v=v: p.feature_is(k, v)))
            else:
                s = arg.symbol
                conditions.append(
                    This.at(Phone, pos, lambda q, s=s: q.is_symbol(s)))

        def run_conditions(td, c=conditions):
            for f in c:
                try:
                    if not f(td):
                        return False
                except IndexError:
                    return False
            return True

        return run_conditions

    def inexpr(self, args):
        current_position = args[0]

        def is_in_position(td, get_current_position=current_position):
            cpos = get_current_position(td)
            if isinstance(cpos, Syllable):
                return td.syllable == cpos
            elif isinstance(cpos, Phone):
                return td.phoneme == cpos
            else:
                return False

        return is_in_position

    def ifexpr(self, args):
        # must only have one argument, a predicate on a transducer
        return args[0]

    def isexpr(self, args):
        entity = args[0]
        value = args[1]
        pred = make_predicate(value)

        def is_true(td, f=entity, pred=pred):
            return pred(f(td))

        return is_true

    def index(self, args):
        counter = args[0]
        raw_pos = args[1]
        if isinstance(raw_pos, tuple):
            position = int(raw_pos[1])
            if counter == "Syllable":

                def get_at_syllable_offset(this, p=position):
                    idx = this.syllables.index(this.syllable)
                    if idx < 0 or idx >= len(this.syllables):
                        return None
                    return this.syllables[this.syllables.index(this.syllable) +
                                          p]

                return get_at_syllable_offset
            elif counter == "Phone":

                def get_at_phoneme_offset(this, p=position):
                    idx = this.phonemes.index(this.phoneme)
                    if idx < 0 or idx >= len(this.phonemes):
                        return None
                    return this.phonemes[this.phonemes.index(this.phoneme) + p]

                return get_at_phoneme_offset
        else:
            position = int(raw_pos)
            if counter == "Syllable":

                def get_at_syllable_index(this, p=position):
                    if p < 0 or p >= len(this.syllables):
                        return None
                    return this.syllables[p]

                return get_at_syllable_index
            elif counter == "Phone":

                def get_at_phoneme_index(this, p=position):
                    if p < 0 or p >= len(this.phonemes):
                        return None
                    return this.phonemes[p]

                return get_at_phoneme_index

    def offset(self, args):
        os = args[0]
        return ("@", os)

    def member(self, args):
        entity = args[0]
        field = args[1]
        if field == 'nucleus':
            return lambda td, f=entity: f(td).get_nucleus()
        elif field == 'onset':
            return lambda td, f=entity: f(td).get_onset()
        elif field == 'coda':
            return lambda td, f=entity: f(td).get_coda()
        elif field == 'quality':

            def get_vowel_quality(td, f=entity):
                # f(td) must produce a vowel!
                e = f(td)
                if isinstance(e, list):
                    vowel = e[0].copy()
                else:
                    vowel = e.copy()
                vowel.set_features_false("long")
                vowel.set_symbol_from_features()
                return vowel

            return get_vowel_quality
        else:
            raise ParseError("Unknown field {}!".format(field))

    def feat_expr(self, args):
        ret = dict()
        for a in flatten(args):
            ret[a[0]] = a[1]
        return ret

    def pos_feature(self, args):
        return [(f, "+") for f in flatten(args)]

    def neg_feature(self, args):
        return [(f, "-") for f in flatten(args)]

    def words(self, args):
        return args

    def fcall(self, args):
        fname = args[0]
        try:
            return self.funcs[fname](*args[1:])
        except KeyError:
            return Change()

    def eqexpr(self, args):
        @ft.singledispatch
        def run_equality(left, right):
            return left == right

        @run_equality.register
        def _(left: Phone, right):
            return left.is_symbol(right.symbol)

        @run_equality.register
        def _(left: type(None), right):
            return False

        return lambda td, args=args: run_equality(args[0](td), args[1](td))
