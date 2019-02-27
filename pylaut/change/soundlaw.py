import importlib
import json as jm
from pylaut.pylautlang import lib


class MissingDataError(Exception):
    pass


class LibraryError(Exception):
    pass


class LibraryVersionError(LibraryError):
    pass


class SoundLaw():
    """
    A wrapper class for a set of sound changes.
    Includes all the nice human-readable information about a sound
    law one might want, and is crucially dated.
    """

    def __init__(self,
                 change_repr,
                 changes,
                 date,
                 sc_lib=None,
                 sc_lib_name=None,
                 sc_lib_version=None,
                 name=None,
                 description=None):
        self.code = change_repr
        self.changes = changes
        self.date = date
        self.sc_lib = sc_lib
        self.sc_lib_name = sc_lib_name
        self.sc_lib_version = sc_lib_version
        self.description = description
        self.name = name

        self.validate()

    @classmethod
    def from_json(cls, json_obj):
        if isinstance(json_obj, str):
            json_obj = jm.loads(json_obj)

        return cls(
            json_obj['code'],
            json_obj['date'],
            sc_lib=json_obj['sc_lib'],
            sc_lib_name=json_obj['sc_lib_name'],
            sc_lib_version=json_obj['sc_lib_version'],
            description=json_obj['description'],
            name=json_obj['name'])

    def __repr__(self):
        return "<SoundLaw {}>".format(self.name)

    def validate(self):

        if not self.sc_lib:
            self.sc_lib = lib.get_library()

        # TODO: we obviously also want to support changes that aren't done
        # with pylautlang, but those have the problem of not being serializable!
        # So for now the solution is to make the user provide a custom pylautlang
        # library that exposes the changes as functions.
        # We may want to make this easier.

        if not isinstance(self.code, str):
            raise TypeError(
                "Expected str, got {}: ".format(type(self.code)),
                "SoundLaw objects must be initialized with "
                "PyLautLang representations of the change!")

        # self.sc_lib = self.sc_lib_from_serializable(self.sc_lib)

        if self.sc_lib_name:
            if not self.sc_lib['__name__'] == self.sc_lib_name:
                raise LibraryError("Specified library {}, but got {}!\n",
                                   "Check your library files.")

        if self.sc_lib_version:
            majorv = self.sc_lib['__version__'].split('.')[0]
            specmv = self.sc_lib_version.split('.')[0]
            if not majorv == specmv:
                raise LibraryVersionError("Specified library version {}, "
                                          "but got {}!\n"
                                          "Check your library files.".format(
                                              self.sc_lib_version,
                                              self.sc_lib['__version__']))

        # try:
        #     self.change = parser.compile(self.code, self.sc_lib,
        #                                  self.featureset)
        # except lark.ParseError as e:
        #     raise ValueError(
        #         "SoundLaw must be initialized with valid PyLautLang!") from e

    def to_json(self, as_dict=False):
        obj = {
            'name': self.name,
            'code': self.code,
            'date': self.date,
            'sc_lib': self.sc_lib_to_serializable_dict(),
            'sc_lib_name': self.sc_lib_name,
            'sc_lib_version': self.sc_lib_version,
            'description': self.description
        }

        if as_dict:
            return obj

        return jm.dumps(obj, indent=2)

    def sc_lib_to_serializable_dict(self):
        obj = {}
        for k, v in self.sc_lib.items():
            if k in ['__name__', '__version__', '__file__', '__module_name__']:
                obj[k] = v
            else:
                obj[k] = v.__name__

        return obj

    def sc_lib_from_serializable(self, sc_lib_dict):
        sc_lib = {}
        try:
            mod = importlib.import_module(sc_lib_dict['__module_name__'])
        except ImportError:
            spec = importlib.util.spec_from_file_location(
                sc_lib_dict['__module_name__'], sc_lib_dict['__file__'])
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

        for k, v in sc_lib_dict.items():
            if k in ['__name__', '__version__', '__file__', '__module_name__']:
                sc_lib[k] = v
            else:
                sc_lib[k] = mod.v

        return sc_lib

    def apply(self, word):
        new_word = word
        for change in self.changes:
            new_word = change.apply(new_word)
        return new_word


class SoundLawGroup(SoundLaw):
    def __init__(self,
                 children,
                 date,
                 sc_lib=None,
                 sc_lib_name=None,
                 sc_lib_version=None,
                 name=None,
                 description=None):
        super().__init__("GROUP", children, date, sc_lib, sc_lib_name,
                         sc_lib_version, name, description)
        self.children = children

        @classmethod
        def from_json(cls, json_obj):
            if isinstance(json_obj, str):
                json_obj = jm.loads(json_obj)

            return cls(
                json_obj['children'],
                json_obj['date'],
                sc_lib=json_obj['sc_lib'],
                sc_lib_name=json_obj['sc_lib_name'],
                sc_lib_version=json_obj['sc_lib_version'],
                description=json_obj['description'],
                name=json_obj['name'])

    def to_json(self, as_dict=False):
        obj = super().to_json(as_dict=True)
        obj['children'] = [c.to_json(as_dict=True) for c in self.children]
        if as_dict:
            return obj
        return jm.dumps(obj, indent=2)
