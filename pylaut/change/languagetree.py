"""
Module languagetree
Defines a class holding the diachronic information for all descendants of a single language
"""

import importlib
import json as jm
import pathlib

from pylaut.language import lexicon
from pylaut.change import change
from pylaut.language.phonology import phonology
from pylaut.pylautlang import parser, lib

import lark


def _jdefault(o):
    if isinstance(o, pathlib.PurePath):
        return str(o)
    return o.to_json()


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
                 date,
                 sc_lib=None,
                 sc_lib_name=None,
                 sc_lib_version=None,
                 name=None,
                 description=None):
        self.code = change_repr
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

    def validate(self):

        if not self.sc_lib:
            self.sc_lib = lib.get_library()

        # TODO: we obviously also want to support changes that aren't done
        # with pylautlang, but those have the problem of not being serializable!
        # So for now the solution is to make the user provide a custom pylautlang
        # library that exposes the changes as functions.
        # We may want to make this easier.

        # if not isinstance(self.code, str):
        #     raise TypeError(
        #         "Expected str, got {}: ".format(type(self.code)),
        #         "SoundLaw objects must be initialized with "
        #         "PyLautLang representations of the change!")

        self.sc_lib = self.sc_lib_from_serializable(self.sc_lib)

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
                'sc_lib': self.sc_lib_to_serializeable_dict(),
                'sc_lib_name': self.sc_lib_name,
                'sc_lib_version': self.sc_lib_version,
                'description': self.description
            }

            if as_dict:
                return obj

            return jm.dumps(obj)

        def sc_lib_to_serializable_dict(self):
            obj = {}
            for k, v in self.sc_lib.items():
                if k in [
                        '__name__', '__version__', '__file__',
                        '__module_name__'
                ]:
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
                if k in [
                        '__name__', '__version__', '__file__',
                        '__module_name__'
                ]:
                    sc_lib[k] = v
                else:
                    sc_lib[k] = mod.v

            return sc_lib


class SoundLawGroup(SoundLaw):
    def __init__(self,
                 children,
                 date,
                 sc_lib=None,
                 sc_lib_name=None,
                 sc_lib_version=None,
                 name=None,
                 description=None):
        super().__init__("/0/ -> /0/", date, sc_lib, sc_lib_name,
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
        return jm.dumps(obj)


class Meta():
    """
    Class representing language metadata.
    This class is essentially a thin wrapper around a
    dictionary that performs some housekeeping to
    make file operations for language trees easier.
    """

    def __init__(self,
                 featureset=None,
                 featureset_path=None,
                 file_path=None,
                 data_path=None,
                 config_file_name=None,
                 change_file_name=None,
                 lexicon_file_name=None,
                 sc_lib=None):

        self.featureset_name = featureset
        self.featureset_path = pathlib.Path(featureset_path)
        self.file_path = pathlib.Path(file_path)
        self.data_path = pathlib.Path(data_path)
        self.config_file_name = config_file_name
        self.change_file_name = change_file_name
        self.lexicon_file_name = lexicon_file_name

    @classmethod
    def from_json(cls, json, is_str=True):
        if is_str:
            obj = jm.loads(json)
        else:
            obj = json

        this = cls(
            featureset=obj['featureset'],
            featureset_path=obj['featureset_path'],
            file_path=obj['file_path'],
            data_path=obj['data_path'],
            config_file_name=obj['config_file_name'],
            change_file_name=obj['change_file_name'],
            lexicon_file_name=obj['lexicon_file_name'])

        return this

    def to_json(self, as_dict=False):
        obj = {
            'file_path': self.file_path,
            'data_path': self.data_path,
            'featureset': self.featureset_name,
            'featureset_path': self.featureset_path,
            'config_file_name': self.config_file_name,
            'lexicon_file_name': self.lexicon_file_name
        }

        if as_dict:
            return obj
        return jm.dumps(obj, indent=2, default=_jdefault)


class LanguageTree():
    """
    Class that represents a language relative to its ancestors,
    descendants, and languages it interacted with.
    """

    def __init__(self, meta=None, name=None, date=0):

        self.meta = meta if meta else Meta()
        self.name = name
        self.date = date
        self.lexicon = None
        self.lexicon_delta = None
        self.phonology = None
        self.changes = []
        self.children = []

    @classmethod
    def from_json(cls, json_str):
        obj = jm.loads(json_str)
        this = cls()
        this.meta = Meta.from_json(obj['meta'], is_str=False)
        this.date = obj['date']
        this.children = obj['children']
        this.lexicon = obj['lexicon']
        this.lexicon_delta = obj['lexicon_delta']
        this.phonology = obj['phonology']
        return this

    def to_json(self, exhaustive=False):
        meta = self.meta.to_json(as_dict=True)
        obj = {
            'meta': meta,
            'date': self.date,
            'children': self.children,
            'lexicon': None,
            'lexicon_delta': None,
            'phonology': None
        }

        if exhaustive:
            if self.lexicon:
                obj['lexicon'] = self.lexicon.to_json()
            if self.lexicon_delta:
                obj['lexicon_delta'] = self.lexicon_delta.to_json()
            if self.phonology:
                obj['phonology'] = self.phonology.to_json()

        return jm.dumps(obj, indent=2, default=_jdefault)

    def write(self):
        if not self.meta.file_path:
            raise MissingDataError('No file path known for language {}'.format(
                self.name))

        with self.meta.file_path.open('w') as of:
            of.write(self.to_json())
