import lark
from lark import Lark, ParseError, Transformer
from pkgutil import get_data
from pylaut.language.phonology.phone import Phone
from pylaut.language.phonology.phonology import Phoneme
from pylaut.language.phonology.word import Syllable
from pylaut.change.change import Change, This, ChangeGroup
from pylaut.change.soundlaw import SoundLaw, SoundLawGroup
from pylaut.change.change_functions import replace_phonemes, change_feature
from pylaut.pylautlang.lib import get_library, make_predicate
import functools as ft

import pathlib

def get_parser():
    pllg = Lark(
        get_data("pylaut", "data/pylautlang.g").decode("utf-8"),
        propagate_positions=True)
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


def compile(scstring, lib=get_library(), featureset=None):
    pll = PyLautLang(lib, featureset)
    change = pll.compile(scstring)
    return change


def parse_file(file_path, lib=get_library(), featureset=None):
    p = pathlib.Path(file_path)
    with p.open('r') as scf:
        scstr = scf.read()
    return compile(scstr, lib, featureset)


def validate(scstring):
    pll = PyLautLang()
    pll.parser.parse(scstring)
    return True


class PyLautLang(Transformer):
    def __init__(self, funcs={}, featureset=None):
        super().__init__()
        self.funcs = funcs
        self.featureset = featureset
        self.parser = get_parser()

    def compile(self, scstring):
        t = self.parser.parse(scstring)
        change = self.transform(t)
        return change

    def start(self, l):
        return l

    def meta(self, args):
        return ('META', args[0], args[1])

    def block(self, children):
        return children

    def group_block(self, args):
        return args

    def law(self, args):
        block = args[-1]
        name = None
        description = None
        date = None
        changes = None
        for meta in args[:-1]:
            varname = meta[1].lower()
            if varname == 'name':
                name = meta[2].value.strip('"')
            elif varname == 'description':
                description = meta[2]
            elif varname == 'date':
                date = meta[2]
        changes = block
        if self.funcs is not None:
            sc_lib_name = self.funcs['__name__']
            sc_lib_version = self.funcs['__version__']
        else:
            sc_lib_name = None
            sc_lib_version = None
        return SoundLaw(
            '',
            changes,
            date,
            sc_lib=self.funcs,
            sc_lib_name=sc_lib_name,
            sc_lib_version=sc_lib_version,
            name=name,
            description=description)

    def group(self, args):
        block = args[-1]
        name = None
        description = None
        date = None
        changes = []
        for meta in args[:-1]:
            varname = meta[1].lower()
            if varname == 'name':
                name = meta[2].value.strip('"')
            elif varname == 'description':
                description = meta[2]
            elif varname == 'date':
                date = meta[2]
        for change in block:
            changes.append(change)
        if self.funcs is not None:
            sc_lib_name = self.funcs['__name__']
            sc_lib_version = self.funcs['__version__']
        else:
            sc_lib_name = None
            sc_lib_version = None
        return SoundLawGroup(
            changes,
            date,
            sc_lib=self.funcs,
            sc_lib_name=sc_lib_name,
            sc_lib_version=sc_lib_version,
            name=name,
            description=description)

    def phoneme(self, l):
        pl = phoneme_list_from_string(l[0])
        return pl

    def phoneme_list(self, l):
        args = []
        if len(l) == 1:
            return l[0]
        for c in l:
            args.append(tuple(c))

        return tuple(args)

    def simple_unconditional(self, args):
        domain = args[0]
        codomain = args[1]
        return replace_phonemes(domain, codomain)

    def multiple_unconditional(self, args):
        domain, codomain = args[0], args[1]

        ch = ChangeGroup(
            [replace_phonemes(d, c) for d, c in zip(domain, codomain)])
        return ch

    def change_feature(self, args):
        domain, codomain = args[0], args[1]
        ch = Change()
        for name, value in codomain.items():
            ch = ch.do(lambda td: change_feature(td.phoneme, name, value))

        def match_features(p, fdict=domain):
            for name, value in domain.items():
                if not p.feature_is(name, value):
                    return False
            return True

        ch = ch.to(This.forall(Phone)(match_features))
        return ch

    def replace_by_feature(self, args):
        domain, codomain = args[0], args[1]
        conditions = []
        for name, value in domain.items():

            def has_feature(p, n=name, v=value):
                return p.feature_is(n, v)

            conditions.append(has_feature)
        ch = Change().do(lambda p: codomain).to(
            This.forall(Phone)(lambda p, c=conditions: all(f(p) for f in c)))
        return ch

    def positive_condition(self, args):
        return args[0]

    def negative_condition(self, args):
        return lambda td: not args[0](td)

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

    def simple_conditional(self, children):
        changes = []

        domain = children[0]
        default = children[-1]
        for (codomain,
             condition) in zip(*[children[1:-2][i::2] for i in range(2)]):
            ch = self.simple_unconditional([domain, codomain])
            ch = ch.when(condition)
            changes.append(ch)
        default_ch = self.simple_unconditional([domain, default])
        changes.append(default_ch)
        return ChangeGroup(changes)

    def multiple_conditional(self, children):
        changes = []

        domain = children[0]
        default = children[-1]
        for (codomain,
             condition) in zip(*[children[1:-2][i::2] for i in range(2)]):
            ch = self.multiple_unconditional([domain, codomain])
            ch = ch.when(condition)
            changes.append(ch)
        default_ch = self.multiple_unconditional([domain, default])
        changes.append(default_ch)
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

    def replace_by_feature_conditional(self, args):
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
        if isinstance(entity, tuple):
            entity = entity[1]

        if field == 'nucleus':
            ret = lambda td, f=entity: f(td).get_nucleus()
        elif field == 'onset':
            ret = lambda td, f=entity: f(td).get_onset()
        elif field == 'coda':
            ret = lambda td, f=entity: f(td).get_coda()
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

            ret = get_vowel_quality
        elif field == 'is_monosyllable':
            ret = lambda td, f=entity: f(td).is_monosyllable()
        else:
            raise ParseError("Unknown field {}!".format(field))

        return ret

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

    def fcall(self, children):
        fname = children[0]
        args = []
        for c in children[1:]:
            args.append(c)
        try:
            return self.funcs[fname](*args)
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

        def ret(td, args=args):
            return run_equality(args[0](td), args[1](td))

        return ret
