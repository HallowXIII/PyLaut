"""
Module languagetree
Defines a class holding the diachronic information for all descendants of a single language
"""

import importlib
import json as jm
import pathlib
from typing import List, Dict, Optional, Union

from pylaut.language import lexicon
from pylaut.change import change
from pylaut.language.phonology import phonology
from pylaut.pylautlang import lib, parser

from pylaut import utils

import lark


def _jdefault(o):
    if isinstance(o, pathlib.PurePath):
        return str(o)
    return o.to_json(as_dict=True)


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
                 lexicon_delta_file_name=None):

        self.featureset_name = featureset
        self.featureset_path = pathlib.Path(
            featureset_path) if featureset_path else None
        self.file_path = pathlib.Path(file_path) if file_path else None
        self.data_path = pathlib.Path(data_path) if data_path else None
        self.config_file_name = config_file_name
        self.change_file_name = change_file_name
        self.lexicon_file_name = lexicon_file_name
        self.lexicon_delta_file_name = lexicon_delta_file_name

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
            lexicon_delta_file_name=obj['lexicon_delta_file_name'],
            lexicon_file_name=obj['lexicon_file_name'])

        return this

    @property
    def lexicon_delta_file_path(self):
        if self.data_path and self.lexicon_delta_file_name:
            return self.data_path / self.lexicon_delta_file_name
        return None

    @property
    def lexicon_file_path(self):
        if self.data_path and self.lexicon_file_name:
            return self.data_path / self.lexicon_file_name
        return None

    @property
    def change_file_path(self):
        if self.data_path and self.change_file_name:
            return self.data_path / self.change_file_name
        return None

    def to_json(self, as_dict=False):
        obj = {
            'file_path': self.file_path,
            'data_path': self.data_path,
            'featureset': self.featureset_name,
            'featureset_path': self.featureset_path,
            'config_file_name': self.config_file_name,
            'lexicon_file_name': self.lexicon_file_name,
            'lexicon_delta_file_name': self.lexicon_delta_file_name,
            'change_file_name': self.change_file_name
        }

        if as_dict:
            return obj
        return jm.dumps(obj, indent=2, default=_jdefault)

    def default(self, family_name):
        if not family_name:
            family_name = 'Family'
        self.data_path = pathlib.Path('.')
        self.file_path = pathlib.Path('.') / '{}.json'.format(family_name)
        self.config_file_name = '{}.cfg'.format(family_name)
        self.lexicon_file_name = '{}.lex'.format(family_name)
        self.lexicon_delta_file_name = None
        self.change_file_name = None
        return self

    def file_prefix(self, prefix):
        self.config_file_name = '{}.cfg'.format(prefix)
        self.lexicon_file_name = '{}.lex'.format(prefix)
        self.lexicon_delta_file_name = '{}.dlex'.format(prefix)
        self.change_file_name = '{}.sc'.format(prefix)
        return self

    def clone(self, keep_file_path=True):
        new = Meta(self.featureset_name, self.featureset_path, self.file_path,
                   self.data_path, self.config_file_name,
                   self.change_file_name, self.lexicon_file_name)
        if not keep_file_path:
            new.file_path = None
        return new


class LanguageTree():
    """
    Class that represents a language relative to its ancestors,
    descendants, and languages it interacted with.
    """

    def __init__(self, name=None, date=0, proto=None, meta=None):

        self.meta = meta if meta else Meta().default(name)
        self.name = name
        self.date = date
        self.proto = proto
        self.lexicon = None
        self.lexicon_delta = None
        self.phonology = None
        self.changes = None
        self.children = []

    @classmethod
    def from_json(cls, json: Union[dict, str]):
        if isinstance(json, str):
            obj = jm.loads(json)
        elif isinstance(json, dict):
            obj = json
        else:
            raise TypeError('Argument to from_json must be a dict'
                            'or a json string!')
        this = cls()
        this.meta = Meta.from_json(obj['meta'], is_str=False)
        this.name = obj['name']
        this.date = obj['date']
        this.children = [cls.from_json(o) for o in obj['languages']]
        this.proto = obj['proto']
        this.lexicon = obj['lexicon']
        this.lexicon_delta = obj['lexicon_delta']
        this.phonology = obj['phonology']
        return this

    @classmethod
    def load(cls, file_path_or_name: str):
        p = pathlib.Path(file_path_or_name)
        if not p.exists():
            p = pathlib.Path(f'{file_path_or_name}.json')
            if not p.exists():
                raise ValueError(f'No such file: {p}. '
                                 'Did you misspell anything?')
        with p.open('r') as jsonf:
            ret = cls.from_json(jsonf.read())
        return ret

    def _load_files(self) -> None:
        dlex_path = self.meta.lexicon_delta_file_path
        lex_path = self.meta.lexicon_file_path
        change_path = self.meta.change_file_path

        if lex_path and lex_path.exists():
            self.lexicon = lexicon.Lexicon.load(lex_path)

        if dlex_path and dlex_path.exists():
            self.lexicon_delta = lexicon.DifferenceLexicon.load(dlex_path)

        if change_path and change_path.exists():
            self.changes = parser.parse_file(change_path)

    def tree(self, indent=2) -> str:
        basic_tree = self.to_json(as_dict=True)

        def _tree(t):
            _t = {
                'name': t['name'],
                'proto': t['proto'],
                'date': t['date'],
                'languages': t['languages']
            }
            _t['languages'] = [_tree(l) for l in _t['languages']]
            return _t

        return jm.dumps(_tree(basic_tree), indent=2)

    def to_json(self, as_dict=False, exhaustive=False) -> Union[dict, str]:
        meta = self.meta.to_json(as_dict=True)
        obj = {
            'name': self.name,
            'proto': self.proto,
            'date': self.date,
            'meta': meta,
            'languages': [c.to_json(as_dict=True) for c in self.children],
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

        if as_dict:
            return obj

        return jm.dumps(obj, indent=2, default=_jdefault)

    def add_node(self, name=None, date=None, proto=None,
                 file_prefix=None) -> None:
        if not proto:
            proto = name
        new = LanguageTree(
            name, date, proto,
            self.meta.clone(False).file_prefix(
                file_prefix if file_prefix else name))
        self.children.append(new)
        return new

    def save(self) -> None:
        if self.meta.file_path:
            # We are a family root node or the user has decided to make us one
            # Save family information
            with self.meta.file_path.open('w') as of:
                of.write(self.to_json())

        # Now for saving language information
        # Sound changes cannot be serialized! So we can only save lexicon
        # information.
        if self.lexicon:
            self.lexicon.save(self.meta.lexicon_file_path)
        if self.lexicon_delta:
            self.lexicon_delta.save(self.meta.lexicon_delta_file_path)

    def _dfs(self, root, node_name: str):
        if root is None:
            root = self
        for c in root.children:
            if c.name == node_name:
                return [root, c]
            r = self._dfs(c, node_name)
            if r:
                r.insert(0, root)
                return r
        return None

    def _build_path(self, root_name: str, node_name: str):
        if root_name is None:
            return self._dfs(None, node_name)
        else:
            return self._dfs(self._dfs(None, root_name)[-1], node_name)

    def simulate(self, node_name: str) -> None:
        path = self._build_path(None, node_name)
        if not path:
            raise ValueError(f'No such node: {node_name}.')
        else:
            for i, node in enumerate(path[1:], start=1):
                origin = path[i - 1]
                this = node
                origin._load_files()
                this._load_files()
                if not this.changes:
                    raise utils.EmptyException(
                        "Cannot simulate changes from "
                        f"{origin.proto} to {this.proto}: "
                        "changes aren't defined!"
                    )
                if this.lexicon_delta:
                    prepared_lexicon = this.lexicon_delta.merge(origin.lexicon)
                else:
                    prepared_lexicon = origin.lexicon
                new_lexicon = prepared_lexicon.run_sound_changes(this.changes)
                new_lexicon.set_date(this.date, 'ER')
                this.lexicon = new_lexicon

    def get_node(self, node_name: str):
        cand = self._dfs(None, node_name)
        ret = cand[-1] if cand else None
        return ret
