from copy import deepcopy
from functools import partial
from pylaut.phone import Phone
from pylaut.phonology import Phonology, Phoneme
from pylaut.word import Word, WordFactory, Syllable
from pylaut.utils import flatten_partial, mapwith, o

class This(object):
    """
    A dummy object for "the current position" in a word. Contains utility
    methods to produce the complicated functions required by a Change object.
    """

    @staticmethod
    def at(kind, position, pred):
        """
        at :: (Type * Int * (WordPart -> Bool)) -> Transducer -> Bool

        Returns a function from a Transducer to the word part of type Type
        at offset `position` from the current word part the change is acting on.
        """
        if kind == Syllable:
            return lambda ch: pred(ch.syllables[
                ch.syllables.index(ch.syllable) + position])
        elif kind == Phone:
            return lambda ch: pred(ch.phonemes[
                ch.phonemes.index(ch.phoneme) + position])
        else:
            raise ValueError("Unknown position type")

    @staticmethod
    def forall(kind):
        """
        forall :: Type -> (WordPart -> Bool) -> Transducer ->
            ((WordPart -> WordPart) * (Transducer -> Bool)) -> Word

        A pretty hacky function that returns a breathtaking mess of lambdas
        internally used by Change objects to pull all the parts of a sound
        change together. Fully applied, it sets off the actual changing
        machinery.
        """
        if kind == Syllable:
            return lambda pred: lambda ch: lambda f, c: ch._run_syl(pred, f, c)
        elif kind == Phone:
            return lambda pred: lambda ch: lambda f, c: ch._run_ph(pred, f, c)
        else:
            raise ValueError("Unknown position type")

    @staticmethod
    def is_at_index(kind, index):
        """
        is_at_index :: (Type * Int) -> Transducer -> Bool

        Function to find a phoneme at an absolute word position. Useful for
        changing e.g. word-initial or word-final sounds.

        Args:
            kind: Which type of word part to look for

            index: The absolute position of the word part within the word,
                as a list index.
        """
        if kind == Syllable:
            return lambda td: td.syllable == td.syllables[index]
        elif kind == Phone:
            return lambda td: td.phoneme == td.phonemes[index]
        else:
            raise ValueError("Unknown position type")


# word -> word
class Change(object):
    """
    Core data structure to represent a sound change.
    Each method takes a change and returns a new one, thus enabling persistence
    and method chaining.
    """

    def __init__(self):
        self.appl = None
        self.changes = None
        self.conditions = []

    def __call__(self, w):
        return self.apply(w)

    def when(self, what):
        """
        when :: (Change * (Transducer -> Bool)) -> Change

        This method is intended to allow for conditioning a sound change on
        properties of word parts at relative locations within (e.g. m > b if the vowel
        of the last syllable is nasalised). It takes a function that fetches
        a word part from a Transducer object and a predicate on the word part.

        For more convenient indication of relative positions, the This class
        provides the at() method, the return value of which may be used as the
        first argument to Change.when().

        Args:
            what: a predicate on a Transducer.

        Returns:
            A new Change object that applies itself to a word part when the
                word part indicated by where satisfies what.

        Example:
            ch.when(This.at(Phone, 0, λ p: p.is_vowel()))
            ch.when(λ td: td.phoneme.is_vowel())
        """
        nc = deepcopy(self)
        nc.conditions.append(what)
        return nc

    def unless(self, what):
        """
        unless :: (Change * (Transducer -> Bool)) -> Change

        when, but with the condition negated
        """
        nc = deepcopy(self)
        nc.conditions.append(lambda x: not what(x))
        return nc

    def to(self, fetcher):
        """
        to :: Change * (Transducer -> (
                  (WordPart -> WordPart) * (Transducer -> Bool)
              ) -> Word) -> Change

        A method to specify the domain of the change. It is intended for use
            with This.forall(), which returns functions of the signature
            required of `fetcher`.

        Args:
            fetcher: A curried function that, given a transducer and two
                functions of the right signature produces a sound changed
                word.

        Returns:
            A new Change object that includes `fetcher` in its domain 
            selection function.

        Example:
            ch.to(This.forall(Phone)(λ p: p.feature_is_false("continuant")))

            This would specify the domain of ch to be all phonemes in a word 
            that satisfy the condition that they are not continuants. 
            The same effect could be achieved by writing:

            ch.to(λ td: λ f, c: td._run_ph(
                λ p: p.feature_is_false("continuant"), f, c))

        """
        nc = deepcopy(self)
        nc.appl = fetcher if nc.appl is None else o(fetcher, nc.appl)
        return nc

    def do(self, changer):
        """
        do :: (Change * (WordPart -> WordPart)) -> Change

        A method to specify the codomain of a change. `changer` must be a
        function that takes a word part and returns a word part of the same kind.

        Example:
        ch.do(λ s: s.copy().set_stressed())

        This would set the change to shift stress to a certain syllable when
            its conditions are met.
        """
        nc = deepcopy(self)
        nc.changes = changer if nc.changes is None else o(changer, nc.changes)
        return nc

    def _eval(self, transducer):
        """
        _eval :: (Change * Transducer) -> Word

        Evaluates self using a Transducer object.
        """
        return self.appl(transducer)(
            self.changes, lambda pos: all((c(pos) for c in self.conditions)))

    def apply(self, word_obj):
        """
        apply :: (Change * Word) -> Word

        Call this method to apply a sound change to a word.
        """
        # TODO: stop this calling back-and-forth fuckness
        return Transducer(word_obj, self)()


class Transducer(object):

    """
    Class for applying sound changes to words. Supports iteration through
    both syllables and phonemes.
    """

    def __init__(self, word, change):
        self.word = word
        self.syllables = self.word.syllables
        self.syllable = self.syllables[0]
        self.phonemes = self.word.phonemes
        self.phoneme = self.phonemes[0]

        self.change = change

    def __call__(self):
        return self.change._eval(self)

    # this is quite unpretty but

    def _run_ph(self, pred, f, cond):
        """
        _run_ph :: (Transducer * (Phoneme -> Bool) *
                    (Phoneme -> Plist[Phoneme]) * (Transducer -> Bool)) -> Word

        Applies a sound change over phonemes to the current word.

        Args:
            pred: A predicate on the current phoneme. Corresponds to the 
                domain of the sound change.

            f: A function that transforms one phoneme into another. The
                   actual change.

            cond: A predicate on the current state on the transducer. This
                allows expressing conditions on e.g. properties of the
                containing syllable, properties of the word, properties 
                of adjacent phonemes etc.

        Returns:
            A new Word object derived from self.word by applying self.change.
        """
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
                clean_syllable = flatten_partial(
                    filter(lambda x: x is not None, new_syllable))
            ns = Syllable(clean_syllable)
            if syllable.is_stressed():
                ns.set_stressed()
            new_syllables.append(ns)
        return Word(new_syllables)

    def _run_syl(self, pred, f, cond):
        """
        _run_syl :: (Transducer * (Syllable -> Bool) *
                     (Syllable -> Plist[Syllable]) * (Transducer -> Bool)
                    ) -> Word

        Applies a sound change over syllables to the current word.

        Args:
            pred: A predicate on the current syllable. Corresponds to the 
                domain of the sound change.

            f: A function that transforms one syllable into another. The
                   actual change.
            cond: A predicate on the current state on the transducer. This
                allows expressing conditions on e.g. relative location of
                the current syllable, properties of the word, properties
                of adjacent syllables etc.

        Returns:
            A new Word object derived from self.word by applying self.change.
        """
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
    pass

if __name__ == '__main__':

    main()
