from pylaut.language.phonology import word, phonology
import random
import pathlib


class Lexicon(object):
    def __init__(self):
        self.language = None
        self.date = None

        self.phonology = None
        self.word_factory = None

        self.entries = list()

    @classmethod
    def load(cls, file_path_or_name):
        p = pathlib.Path(file_path_or_name)
        if not p.exists():
            p = pathlib.Path(f'{file_path_or_name}.lex')
            if not p.exists():
                raise ValueError(
                    f'No such file: {p}. Did you misspell anything?')
        with p.open('r') as lexf:
            lexicon = cls()
            lexicon.from_string(lexf.read())
        return lexicon

    def save(self, file_name_or_path: str) -> None:
        p = pathlib.Path(file_name_or_path)
        with p.open('w') as outf:
            outf.write(f"#{self.language}\n")
            outf.write("#IPA Orthography Gloss\n")
            outf.writelines(e._serialize() for e in self.entries)

    def get_random_entry(self):
        return random.choice(self.entries)

    def get_random_entry_with_segment(self, segment):
        rand_entry = ""
        while segment not in rand_entry.__repr__():
            rand_entry = self.get_random_entry()
        return rand_entry

    def from_string(self, raw_lexicon):
        read_words = [x for x in raw_lexicon.splitlines() if x and x[0] != "#"]
        split_words = [x.split() for x in read_words]

        # make Lexicons
        for line in split_words:
            self.add_entry(LexiconEntry(*line))

        self.init_phonology()

    def set_date(self, value, system):
        self.date = (value, system)

    def add_entry(self, lexicon_entry):
        self.entries += [lexicon_entry]

    def init_phonology(self):
        # extract phonemes
        phonemes = set()

        self.factory = word.WordFactory()

        for entry in self.entries:
            entry.set_phonetic(self.factory.make_word(entry.ipa))

        for entry in self.entries:
            for syllable in entry.phonetic.syllables:
                for phoneme in syllable:
                    phonemes.add(phoneme.symbol)

        self.phonology = phonology.Phonology(list(phonemes))

    def merge(self, other):
        new = Lexicon()
        new.entries = self.entries + other.entries
        return new

    def run_sound_changes(self, changes):
        new = Lexicon()
        new.entries = [e.run_sound_changes(changes) for e in self.entries]
        return new


class LexiconEntry(object):
    def __init__(self, ipa_string, ortho_string, gloss, date=None):
        self.ipa = ipa_string
        self.orthography = ortho_string
        self.gloss = gloss
        self.date = date
        self.phonetic = None

    def lexicon_entry(self):
        return f"{self.orthography} {self.__repr__()}: {self.gloss}"

    def _serialize(self):
        phonetic = repr(self).strip("*/[]<>")
        orthography = self.orthography
        gloss = self.gloss
        return f"{phonetic} {orthography} {gloss}\n"

    def __repr__(self):
        if self.phonetic:
            return str(self.phonetic)
        else:
            return "*/" + self.ipa + "/"

    def set_phonetic(self, phonetic_word):
        self.phonetic = phonetic_word

    def set_date(self, value, system):
        self.date = (value, system)

    def run_sound_changes(self, changes):
        if not self.phonetic:
            raise ValueError("Could not run sound changes: "
                             "no word objects instantiated.")
        else:
            new = LexiconEntry(self.ipa, self.orthography, self.gloss,
                               self.date)
            w = self.phonetic
            for ch in changes:
                w = ch.apply(w)
            new.set_phonetic(w)
            return new
