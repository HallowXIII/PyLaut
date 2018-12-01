from pylaut.change.change import *
from pylaut.change.change_functions import *
from pylaut.language.phonology.phone import Phone


def make_predicate(parser_entity):
    predicate = lambda _: True
    if isinstance(parser_entity, dict):
        predicates = []
        for k, v in parser_entity.items():
            predicates.append(lambda p, k=k, v=v: p.feature_is(k, v))

        def feature_predicate(p, predicates=predicates):
            for f in predicates:
                if not f(p):
                    return False
            return True

        predicate = feature_predicate
    elif isinstance(parser_entity, Phone):

        def phone_predicate(p, t=parser_entity):
            return p.is_symbol(t.symbol)

        predicate = phone_predicate
    elif isinstance(parser_entity, str):

        def symbol_predicate(p, t=parser_entity):
            return p.is_symbol(t)

        predicate = symbol_predicate
    elif isinstance(parser_entity, tuple):
        predicates = []
        for t in parser_entity:
            predicates.append(lambda p, t=t: p.is_symbol(t.symbol))

        def list_predicate(p, t=predicates):
            return all(f(p) for f in t)

        predicate = list_predicate
    elif isinstance(parser_entity, list):
        return make_predicate(parser_entity[0])

    return predicate


def metathesis(left, right):
    pl = make_predicate(left)
    pr = make_predicate(right)

    def exchange(this):
        current = this.phonemes.index(this.phoneme)
        sylidx = this.syllable.phonemes.index(this.phoneme)
        try:
            next = this.phonemes[current + 1]
        except IndexError:
            return
        this.phonemes[current] = next
        this.phonemes[current + 1] = this.phoneme
        this.syllable.phonemes[sylidx] = next
        try:
            this.syllable.phonemes[sylidx + 1] = this.phoneme
        except IndexError:
            cursyl = this.syllables.index(this.syllable)
            this.syllables[cursyl + 1].phonemes[0] = this.phoneme
        this.advance()
        return next

    def defer(this):
        return exchange(this)

    return Change().do(defer).to(This.forall(Phone)(pl)).when(
        This.at(Phone, 1, pr))


def lengthen(phone):
    return Change().do(
        lambda this: change_feature(this.phoneme, "long", True)).to(
            This.forall(Phone)(make_predicate(phone)))


def intervocal_voicing(this):
    return Change().do(
        lambda this: change_feature(this.phoneme, "voice", True)).to(
            This.forall(Phone)(make_predicate(this))).when(
                This.at(Phone, -1, lambda p: p.is_vowel())).when(
                    This.at(Phone, 1, lambda p: p.is_vowel()))


def merge(phonemes, target):
    target = target[0]
    phonemes = [p[0] for p in phonemes]
    return Change().do(lambda _: target).to(
        This.forall(Phone)(
            lambda p: any(p.is_symbol(b.symbol) for b in phonemes)))


def epenthesis(this, phoneme):
    p = make_predicate(this)

    def epenthesize(td, p=p, t=phoneme):
        if p(td.phoneme):
            cur_idx = td.phonemes.index(td.phoneme)
            syl_idx = td.syllable.phonemes.index(td.phoneme)
            td.phonemes.insert(cur_idx + 1, t)
            td.syllable.phonemes.insert(syl_idx + 1, t)
            td.advance()
            return td.phoneme
        return td.phoneme

    return Change().do(epenthesize).to(This.forall(Phone)(p))


def resyllabify(*args):
    return Resyllabify()


def get_library():
    library = {
        "__name__": "libpylautlang",
        "__version__": "0.1.0",
        "__file__": __file__,
        "__module_name__": __name__,
        "Metathesis": metathesis,
        "Lengthen": lengthen,
        "IntervocalVoicing": intervocal_voicing,
        "Merge": merge,
        "Epenthesis": epenthesis,
        "Resyllabify": resyllabify
    }

    return library
