"""
This module defines a class for translating a PyLaut program into executable
code, as well as some convenience functions for easily accessing the PyLaut
language.
"""

import functools as ft
import pathlib
from pkgutil import get_data
from typing import Callable, Dict, List, Optional, Tuple, Union

from lark import Lark, ParseError, Transformer

from pylaut.change import change_functions
from pylaut.change.change import Change, ChangeGroup, This, Transducer
from pylaut.change.soundlaw import SoundLaw, SoundLawGroup
from pylaut.language.phonology.phone import Phone
from pylaut.language.phonology.phonology import Phoneme
from pylaut.language.phonology.word import Syllable
from pylaut.pylautlang.lib import get_library, make_predicate

Features = Dict[str, str]
PhonemeList = List[Phoneme]
PyLautAtom = Union[Phoneme, PhonemeList, Features]
Library = Dict[str, Callable[[PyLautAtom], PyLautAtom]]


def get_parser():
    """
    A convenience function to create a Lark parser for the PyLaut language
    and return it. The grammar for the PyLaut language is loaded from the
    package data.

    :returns: A Lark parser.
    """
    pllg = Lark(
        get_data("pylaut", "data/pylautlang.g").decode("utf-8"),
        propagate_positions=True)
    return pllg


def phoneme_list_from_string(s: str) -> List[Phoneme]:
    """
    An ad-hoc tokenizing function that creates a list of Phonemes from
    an IPA string. Returns a tuple of Phoneme objects; the zero Phoneme
    returns an empty tuple, a single phoneme a singleton, and so on.

    :param str s: An IPA string representing one or more phonemes.
    :returns: A tuple of zero or more Phoneme objects.
    """
    p = Phoneme()
    ret = []
    curr = []
    for ch in s:
        if curr == []:
            curr.append(ch)
        elif ch in p.feature_model._ipa_diacritics:
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


def flatten(lst: List[List[object]]) -> List[object]:
    """
    Flattens a list of lists by one level.

    :param list lst: A list of lists.
    """
    return [item for sublist in lst for item in sublist]


def compile(scstring: str,
            lib: Library = get_library(),
            featureset: Optional[str] = None) -> List[SoundLaw]:
    """
    A convenience function that parses a sound change string,
    transforms it into a list of SoundLaw objects and returns the list.

    :param str scstring: A PyLaut language program.
    :param dict lib: The sound change function library to use for this
                     compilation, in the form of a function name to function
                     object dictionary.
    :param FeatureSet featureset: A featureset object to use instead of the
                                  default one.
    :returns: A list of Sound Law objects.
    """
    pll = PyLautLang(lib, featureset)
    change = pll.compile(scstring)
    return change


def compile_one(scstring: str,
                lib: Library = get_library(),
                featureset: Optional[str] = None) -> SoundLaw:
    """
    This function acts like compile, but instead of outputting a list
    of sound laws, will output only one SoundLaw object. Convenient
    for programs that will generate only one.

    :param str scstring: A PyLaut language program.
    :param dict lib: The sound change function library to use for this
                     compilation, in the form of a function name to function
                     object dictionary.
    :param FeatureSet featureset: A featureset object to use instead of the
                                  default one.
    :returns: A Sound Law object.
    """
    pll = PyLautLang(lib, featureset)
    change = pll.compile(scstring)
    return change[0]


def parse_file(file_path: str,
               lib: Library = get_library(),
               featureset: Optional[str] = None) -> List[SoundLaw]:
    """
    Function that loads a PyLaut language program from disk,
    then compiles it into a list of sound changes.

    :param str file_path: The path to a PyLaut language program.
    :param dict lib: The sound change function library to use for this
                     compilation, in the form of a function name to function
                     object dictionary.
    :param FeatureSet featureset: A featureset object to use instead of the
                                  default one.
    :returns: A list of Sound Law objects.
    """
    p = pathlib.Path(file_path)
    with p.open('r') as scf:
        scstr = scf.read()
    return compile(scstr, lib, featureset)


def validate(scstring: str) -> bool:
    """
    A function that checks whether a given PyLaut language program is
    syntactically valid. This function will not catch ParseErrors, so
    care must be taken when using it in scripts and programs.

    :param str scstring: A PyLaut language program.
    :returns: True, or else raises an Error.
    """
    pll = PyLautLang()
    pll.parser.parse(scstring)
    return True


class PyLautLang(Transformer):
    """
    This class defines the methods that turn a Lark-generated PyLaut language
    parse tree into executable sound change objects. Each method translates
    the node of the same name in the grammar.
    """

    def __init__(self, funcs={}, featureset=None):
        super().__init__()
        self.funcs = funcs
        self.featureset = featureset
        self.parser = get_parser()

    def compile(self, scstring: str) -> List[SoundLaw]:
        """
        Convenience method that unifies the steps of parsing and transforming
        inside a single method. Delegated to by all of the module-level
        compile functions.

        :param str scstring: A PyLaut language program.
        :returns: A list of SoundLaw objects.
        """
        t = self.parser.parse(scstring)
        change = self.transform(t)
        return change

    def start(self, l: List[SoundLaw]) -> List[SoundLaw]:
        """
        This method parses an entire PyLaut language program.
        Since the parse is bottom-up, the argument to this is
        simply a list of SoundLaw objects. In consequence, it
        just returns them.

        :param list l: A list of SoundLaw objects.
        :returns: The same list.
        """
        return l

    def meta(self, args: List[str]) -> Tuple[str, str, str]:
        """
        Translates the Meta tags of sound law nodes. The actual information
        assignment is done in those methods, so this just takes the tokens and
        makes them into a convenient tuple.

        :param list args: A list containing tag name and text.
        :returns: A tuple of the arguments prefixed by "META".
        """
        return ('META', args[0], args[1])

    def block(self, children: List[Change]) -> List[Change]:
        """
        Translates the contents of a sound law. Since the parse is bottom-up,
        this will be a list of change objects, so all that needs to be done is
        to return them.

        :param list children: A list of Change objects.
        :returns: The same list.
        """
        return children

    def group_block(self, children: List[SoundLaw]) -> List[SoundLaw]:
        """
        Translates the contents of a sound law group. Works exactly the same
        way as the normal block method, except for the argument type.

        :param list children: A list of SoundLaw objects.
        :returns: The same list.
        """
        return children

    def law(self,
            args: List[Union[Tuple[str, str], List[Change]]]) -> SoundLaw:
        """
        Translates an entire sound law from CHANGE to END. Creates a SoundLaw
        object, assigns the meta data and returns it.

        :param list args: A list of meta tags, with the final element of the
                          list being itself a list of changes.
        :returns: A SoundLaw object.
        """
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

    def group(self, args: List[Union[Tuple[str, str], List[SoundLaw]]]
              ) -> SoundLawGroup:
        """
        Works exactly like the law method, except that it translates a group
        of sound laws rather than sound changes.

        :param list args: A list of meta tags, with the final element of the
                          list being itself a list of changes.
        :returns: A Group object.
        """
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

    def phoneme(self, l: List[str]) -> Tuple[Phoneme]:
        """
        Method to translate phoneme expressions. See the documentation
        of phoneme_list_from_string for more.

        :param l: A list whose sole element is an IPA string.
        :returns: A tuple of phonemes.
        """
        pl = phoneme_list_from_string(l[0])
        return pl

    def phoneme_list(self, l: List[Tuple[Phoneme]]) -> Tuple[Tuple[Phoneme]]:
        """
        Method for translating phoneme lists. Simply returns a tuple of
        translated phoneme expressions, that is, a tuple of tuples.

        :param l: A list of phoneme tuples.
        :returns: A tuple of tuples.
        """
        args = []
        if len(l) == 1:
            return l[0]
        for c in l:
            args.append(tuple(c))

        return tuple(args)

    def simple_unconditional(self, args: List[Phoneme]) -> Change:
        """
        Translates the most basic sound change. The call to replace_phonemes
        is a standard to be able to deal with multiple-phoneme domains; it
        creates a change that will search out and replace any instance of
        the passed sequence of phonemes -- vanilla Change objects can only
        do the one.

        :param list args: Two phonemes.
        :returns: A Change object.
        """
        domain = args[0]
        codomain = args[1]
        return change_functions.replace_phonemes(domain, codomain)

    def multiple_unconditional(self, args: List[Phoneme]) -> Change:
        """
        simple_unconditional, but for phoneme lists. Works exactly the
        same way, but the domain and codomain are zipped together to create
        one change per phoneme pair.

        :param list args: Two phoneme lists.
        :returns: A Change object.
        """
        domain, codomain = args[0], args[1]

        ch = ChangeGroup([
            change_functions.replace_phonemes(d, c)
            for d, c in zip(domain, codomain)
        ])
        return ch

    def change_feature(self, args: List[Features]) -> Change:
        """
        This translates unconditional changes where the domain and codomain
        are both feature expressions. The change_feature function from the
        change_functions module is used to change each feature individually.
        Finally, the created change object is given the condition of a
        predicate that matches the feature values passed in for the domain.

        :param list args: Two feature expressions, parsed into dictionaries.
        :returns: A Change object.
        """
        domain, codomain = args[0], args[1]
        ch = Change()

        def change_features_td(td, cd=codomain):
            p = change_functions.change_features_map(td.phoneme, cd)
            return p

        ch = ch.do(change_features_td)

        def match_features(p, fdict=domain):
            """
            Function that closes over the change domain.
            Matches the domain feature values with the
            target phoneme's features.
            """
            for name, value in fdict.items():
                if not p.feature_is(name, value):
                    return False
            return True

        ch = ch.to(This.forall(Phone)(match_features))
        return ch

    def replace_by_feature(
            self, args: List[Union[Features, Tuple[Phoneme]]]) -> Change:
        """
        This method translates changes where the domain is a feature expression
        and the codomain is a phoneme. Essentially the same as change_feature,
        but with a simpler change result.

        :param list args: A feature dictionary and a tuple of phonemes.
        :returns: A Change object.
        """
        domain, codomain = args[0], args[1]

        def match_features(p, fdict=domain):
            """
            Function that closes over the change domain.
            Matches the domain feature values with the
            target phoneme's features.
            """
            for name, value in fdict.items():
                if not p.feature_is(name, value):
                    return False
            return True

        ch = Change().do(lambda p: codomain).to(
            This.forall(Phone)(match_features))
        return ch

    def positive_condition(self, args: List[Callable[[Transducer], bool]]):
        """
        Dummy node function for non-negated conditions.
        Delegates straight through to the actual condition.

        :param list args: A list with one element, a predicate.
        :returns: A predicate.
        """
        return args[0]

    def negative_condition(self, args):
        """
        Method to translate negated conditions. Calls the condition argument
        and then reverses the result.

        :param list args: A list with one element, a predicate.
        :returns: A predicate.
        """
        return lambda td: not args[0](td)

    def and_condition(self, args):
        """
        The and_condition and or_condition methods simply take the conditions
        and tag them with booleans to allow them to be grouped together
        afterward.

        :param list args: A list with one element, a predicate.
        :returns: A predicate.
        """
        return (True, args[0])

    def or_condition(self, args):
        """
        The and_condition and or_condition methods simply take the conditions
        and tag them with booleans to allow them to be grouped together
        afterward.

        :param list args: A list with one element, a predicate.
        :returns: A predicate.
        """
        return (False, args[0])

    def condition_list(self, args):
        """
        Translates the condition list for a conditional change.
        Separates the conditions into two lists by tag, then
        returns a predicate that runs both lists over every position in the
        transducer, given the condition that if they exist, EVERY and condition
        must be true, and AT LEAST ONE OF the or conditions must be true.

        :param list args: A list containing several conditions.
        :returns: A predicate.
        """
        and_conditions = []
        or_conditions = []
        for sigil, condition in args:
            if sigil:
                and_conditions.append(condition)
            else:
                or_conditions.append(condition)

        def predicate(td, ac=and_conditions, oc=or_conditions):
            """
            Function that closes over condition lists and runs them
            on its transducer argument.
            """

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
        """
        Translates any basic conditional changes by simply adding
        a condition to the underlying base change. Also used as a helper method
        by other sound change translation methods.

        :param list args: A Change object and a predicate.
        :returns: The same change object, with the predicate in its conditions.
        """

        base_change = args[0]
        condition = args[1]
        new_change = base_change.when(condition)
        return new_change

    def simple_conditional(self, children):
        """
        Translates phoneme-to-phoneme alternative-default changes. The way the
        arguments are passed is inconvenient since Python will not allow
        arbitrary list unpacking, thus the convoluted zip expression. The
        way this works is just by creating a conditional change for each
        alternative plus an unconditional one for the default, and returning
        them all as a ChangeGroup object.

        :param list children: The list of change parameters.
        :returns: A ChangeGroup object.
        """
        changes = []

        domain = children[0]
        default = children[-1]

        # the arguments are passed as:
        # [domain, codom, cond, codom, cond, ... , default]
        # the zip expression below essentially splits the list of codomains
        # and conditions into two list and then zips them into pairs.
        #
        # Example:
        # >>> args = [1, 2, 3, 4, 5, 6]
        # >>> args[1:-1]
        # [2, 3, 4, 5]
        # >>> args[1:-1][1::2]
        # [2, 4]
        # >>> [args[1:-1][i::2] for i in range(2)]
        # [[2, 4], [3, 5]]
        # >>> list(zip(*[args[1:-1][i::2] for i in range(2)]))
        # [(2, 3), (4, 5)]
        for (codomain,
             condition) in zip(*[children[1:-1][i::2] for i in range(2)]):
            ch = self.simple_unconditional([domain, codomain])
            ch = ch.when(condition)
            changes.append(ch)
        default_ch = self.simple_unconditional([domain, default])
        changes.append(default_ch)
        return ChangeGroup(changes)

    def multiple_conditional(self, children):
        """
        Same as simple_conditional, but for phoneme list to phoneme list
        changes.

        :param list children: The list of change parameters.
        :returns: A ChangeGroup object.
        """
        changes = []

        domain = children[0]
        default = children[-1]
        for (codomain,
             condition) in zip(*[children[1:-1][i::2] for i in range(2)]):
            ch = self.multiple_unconditional([domain, codomain])
            ch = ch.when(condition)
            changes.append(ch)
        default_ch = self.multiple_unconditional([domain, default])
        changes.append(default_ch)
        return ChangeGroup(changes)

    def change_feature_conditional(self, args):
        """
        Same as simple_conditional, but for feature expression to feature
        expression changes.

        :param list children: The list of change parameters.
        :returns: A ChangeGroup object.
        """
        changes = []

        domain = args[0]
        default = args[-1]
        for (codomain,
             condition) in zip(*[args[1:-1][i::2] for i in range(2)]):
            base_ch = self.change_feature([domain, codomain])
            cond_ch = self.basic_conditional([base_ch, condition])
            changes.append(cond_ch)
        changes.append(self.change_feature([domain, default]))
        return ChangeGroup(changes)

    def replace_by_feature_conditional(self, args):
        """
        Same as simple_conditional, but for feature expression to phoneme
        changes.

        :param list children: The list of change parameters.
        :returns: A ChangeGroup object.
        """
        changes = []

        domain = args[0]
        default = args[-1]
        for (codomain,
             condition) in zip(*[args[1:-1][i::2] for i in range(2)]):
            base_ch = self.replace_by_feature([domain, codomain])
            cond_ch = self.basic_conditional([base_ch, condition])
            changes.append(cond_ch)
        changes.append(self.replace_by_feature([domain, default]))
        return ChangeGroup(changes)

    def relative_expr(self, args):
        """
        This method translates relative position expressions in sound change
        conditions. It is quite convoluted, due to the fact that there are
        many different ways to construct a relative expression and argument
        types may be freely mixed.

        :param list args: The list of position parameters.
        :returns: A predicate function on a transducer.
        """
        # First, check if there are word boundaries specified
        # If yes, check if they are in a legal position.
        # If still yes, set a flag.
        conditions = []
        wordbreak = None
        if "#" in args:
            if args[0] == "#":
                wordbreak = 1
                args = args[1:]
            elif args[-1] == "#":
                wordbreak = -1
                args = args[:-1]
            else:
                raise ParseError("Relative Expr contains '#' that is not at "
                                 "the edge of the expression.")

        this = args.index("_")

        for i in range(len(args)):
            pos = i - this
            arg = args[i]
            # If the argument is a phoneme, we must unpack it.
            if isinstance(arg, list):
                arg = arg[0]
            if isinstance(arg, tuple):
                arg = arg[0]
            if isinstance(arg, str):
                # If the argument is the current position indicator
                # and there is a word break specified: add a check whether
                # the current phoneme is at the correct offset from the
                # word break.
                if arg == "_":
                    if wordbreak:
                        if wordbreak > 0:
                            conditions.append(This.is_at_index(Phone, i))
                        else:
                            relpos = -(len(args) - i)
                            conditions.append(This.is_at_index(Phone, relpos))
                # Otherwise, assume the string is a phone written without
                # slashes.
                else:
                    for p in arg:
                        conditions.append(
                            This.at(Phone, pos, lambda q, p=p: q.is_symbol(p)))
            elif isinstance(arg, dict):
                # If the argument is a dictionary, we have a feature expression
                # Match the features according to the expression
                for k, v in arg.items():
                    conditions.append(
                        This.at(
                            Phone,
                            pos, lambda p, k=k, v=v: p.feature_is(k, v)))
            else:
                # The argument is a Phone
                # Perform by-symbol matching
                s = arg.symbol
                conditions.append(
                    This.at(Phone, pos, lambda q, s=s: q.is_symbol(s)))

        def run_conditions(td, c=conditions):
            """
            Function that closes over the condition list
            from the relative expression translation.
            """
            for f in c:
                try:
                    if not f(td):
                        return False
                except IndexError:
                    return False
            return True

        return run_conditions

    def inexpr(self, args):
        """
        Translates an in-expression. This checks whether the current phone or
        syllable is in a specified absolute position within the word.

        :param list args: The list of position parameters.
        :returns: A predicate function on a transducer.
        """
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
        """
        Translates an if-expression. These only serve to mark boolean
        expression conditions and thus delegate through. Must only have
        one argument, a predicate on a transducer.

        :param list args: The list of position parameters.
        :returns: A predicate function on a transducer.
        """
        return args[0]

    def isexpr(self, args):
        """
        Translates an is-expression. This works by using the lib.make_predicate
        function to switch on the type of the argument and make a predicate,
        then closing over it with a function that will run the predicate on a
        Transducer. The first argument must be a function that, when given a
        transducer, produces something of the same type as the second argument.

        :param list args: A fetcher function and a value to compare to its
                          result.
        :returns: A predicate function on a transducer.
        """

        entity = args[0]
        value = args[1]
        pred = make_predicate(value)

        def is_true(td, f=entity, pred=pred):
            return pred(f(td))

        return is_true

    def index(self, args):
        """
        Translates index expressions. These come in four variants: Phone or
        Syllable array, and absolute or offset index. In any case the return
        value is a function that will fetch the appropriate item from the
        Transducer.

        :param list args: Which array to look in, and at what position.
        :returns: A fetcher function on a transducer.
        """
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
                    rel = idx + p
                    if rel < 0 or rel >= len(this.phonemes):
                        return Phoneme.empty()
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

    def offset(self, args: int) -> Tuple[str, int]:
        """
        Translates relative index expressions. Basically a tagged integer to
        make it possible for the index method to switch on the argument type.
        """
        os = args[0]
        return ("@", os)

    def member(self, args: List[Union[Callable[[Transducer], PyLautAtom], str]]
               ) -> Callable[[PyLautAtom], PyLautAtom]:
        """
        Translates member access on transducer data. Right now all the
        legal options are hard-coded in. In the future, it might be
        desirable to translate everything down into direct method calls
        using the same nomenclature, allowing featuresets / phone subclasses
        to provide them or not.

        :param list args: a fetcher function and a string indicated what should
                          be fetched from its result.
        :returns: Another fetcher function.
        """
        entity = args[0]
        field = args[1]
        if isinstance(entity, tuple):
            entity = entity[1]

        if field == 'nucleus':

            def ret(td, f=entity):
                return f(td).get_nucleus()
        elif field == 'onset':

            def ret(td, f=entity):
                return f(td).get_onset()
        elif field == 'coda':

            def ret(td, f=entity):
                return f(td).get_coda()
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

            def ret(td, f=entity):
                return f(td).is_monosyllable()
        else:
            raise ParseError("Unknown field {}!".format(field))

        return ret

    def feat_expr(self, args):
        """
        Translates feature expressions into dictionaries.

        :param list args: A list of lists of key-value tuples.
        """
        ret = dict()
        for a in flatten(args):
            ret[a[0]] = a[1]
        return ret

    def pos_feature(self, args):
        """
        Translates positive features into a list of tuples.
        """
        return [(f, "+") for f in flatten(args)]

    def neg_feature(self, args):
        """
        Translates negative features into a list of tuples.
        """
        return [(f, "-") for f in flatten(args)]

    def words(self, args: str) -> str:
        """Translates bare-word text."""
        return args

    def fcall(self,
              children: List[Union[str, Optional[PyLautAtom]]]) -> Change:
        """
        Looks up a function name in the function library,
        a dictionary passed to the PyLautLang object at init time.
        If the function exists, call it. If not, return an empty
        Change.

        :param list children: A function name plus the arguments to it.
        :returns: A Change object.
        """
        fname = children[0]
        args = []
        for c in children[1:]:
            args.append(c)
        try:
            return self.funcs[fname](*args)
        except KeyError:
            return Change()

    def eqexpr(self, args: List[Optional[PyLautAtom]]
               ) -> Callable[[Transducer], bool]:
        """
        Translate equality expressions. Uses singledispatch to
        switch on the type of the argument and produce equality
        predicates for the right type.

        :param list children: Two things to compare.
        :returns: A predicate on a transducer.
        """

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
