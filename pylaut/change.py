from copy import deepcopy
from functools import partial, singledispatch
from pylaut.phone import Phone
from pylaut.phonology import Phonology, Phoneme
from pylaut.word import Word, WordFactory, Syllable
from pylaut.utils import change_feature, fand, mapwith, o


class This(object):
    """
    A dummy object for "the current position".
    """

    def __init__(self):
        pass

    @staticmethod
    def at(kind, position):
        if kind == Syllable:
            return lambda ch: ch.syllables[ch.syllables.index(ch.syllable) + position]
        elif kind == Phone:
            return lambda ch: ch.phonemes[ch.phonemes.index(ch.phoneme) + position]
        else:
            raise ValueError("Unknown position type")

    @staticmethod
    def forall(kind):
        if kind == Syllable:
            return lambda pred: lambda ch: lambda f, c: ch._run_syl(pred, f, c)
        elif kind == Phone:
            return lambda pred: lambda ch: lambda f, c: ch._run_ph(pred, f, c)
        else:
            raise ValueError("Unknown position type")
        

# word -> word
class Change(object):

    def __init__(self):
        self.appl = None
        self.changes = None
        self.conditions = []

    def when(self, where, what):
        nc = deepcopy(self)
        nc.conditions.append(o(what, where))
        return nc

    def unless(self, where, what):
        nc = deepcopy(self)
        nc.conditions.append(lambda x: not what(where(x)))
        return nc

    def to(self, fetcher):
        nc = deepcopy(self)
        nc.appl = fetcher if nc.appl is None else lambda w: fetcher(nc.appl(w))
        return nc

    def do(self, changer):
        nc = deepcopy(self)
        nc.changes = changer if nc.changes is None else lambda w: changer(nc.changes(w))
        return nc

    def _eval(self, position):
        return self.appl(position)(
            self.changes, lambda pos: all((c(pos) for c in self.conditions)))

    def apply(self, word_obj):
        return Transducer(word_obj, self)()

    
class Transducer(object):

    def __init__(self, word, change):
        self.word = word
        self.syllables = self.word.syllables
        self.syllable = self.syllables[0]
        self.phonemes = [ph for syl in self.word.phonemes for ph in syl]
        self.phoneme = self.phonemes[0]

        self.change = change

    def __call__(self):
        return self.change._eval(self)

    # this is quite unpretty but

    def _run_ph(self, pred, f, cond):
        new_syllables = []
        for syllable in self.word:
            self.syllable = syllable
            new_syllable = []
            for phoneme in syllable:
                self.phoneme = phoneme
                try:
                    np = f(phoneme) if pred(phoneme) and cond(self) else phoneme
                except IndexError:
                    np = phoneme
                new_syllable.append(np)
            ns = Syllable(new_syllable)
            if syllable.is_stressed():
                ns.set_stressed()
            new_syllables.append(ns)
        return Word(new_syllables)

    def _run_syl(self, pred, f, cond):
        new_syllables = []
        for syllable in self.word:
            self.syllable = syllable
            try:
                new_syllable = (f(syllable) if pred(syllable) and cond(self)
                                else syllable)
            except IndexError:
                new_syllable = syllable
            ns = Syllable(new_syllable)
            if syllable.is_stressed():
                ns.set_stressed()
            new_syllables.append(ns)
        return Word(new_syllables)
    

def main():
    
    phonemes = ["p","t","k",
                "b","d","ɡ",
                "m","n",
                "s","f","x",
                "w","j",
                "r","l",
                "a","e","i","o","u"]
    phonology = Phonology(phonemes)

    wf = WordFactory(phonology)

    raw_words = ["a'sap", "be'ko.mu", "uk.tu'ku"]
    words = [wf.make_word(rw) for rw in raw_words]

    ch = Change().do(lambda x: Phoneme("v")).to(This.forall(Phone)(
        lambda p: p.is_symbol("b"))).when(
            This.at(Syllable, 1), lambda a: a.is_stressed())

    c2 = Change().do(lambda p: change_feature(p, "voice", True)).to(
        This.forall(Phone)(lambda p: p.feature_is_false("continuant"))).when(
            This.at(Phone, -1), lambda p: p.is_vowel()).when(
                This.at(Phone, 1), lambda p: p.is_vowel())

    changed = list(map(c2.apply, map(ch.apply, words)))
    print(changed)


if __name__ == '__main__':

    main()
