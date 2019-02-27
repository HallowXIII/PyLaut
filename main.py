"""
A CLI interface to the PyLaut APIs.
"""

import plac
import os
import pathlib

from pylaut.change import languagetree as lt
from pylaut.pylautlang import parser

commands = ["init", "node", "simulate"]


def _hamming_candidate(name, commands):
    return "dummy"


def _create_languagetree_node(name,
                              date,
                              project_name,
                              project_path=None,
                              data_path=None,
                              parent=None,
                              meta=None):
    if not project_path:
        this_project_path = pathlib.Path(project_name).resolve()
    else:
        this_project_path = pathlib.Path(project_path).resolve()

    if not data_path:
        this_data_path = this_project_path / 'data'
    else:
        this_data_path = pathlib.Path(data_path).resolve()

    if not meta:
        if not parent:
            this_meta = lt.Meta(
                data_path=this_data_path,
                config_file_name='{}.cfg'.format(project_name),
                change_file_name='{}.sc'.format(name),
                lexicon_file_name='{}.lex'.format(project_name))
        else:
            parent_json = this_project_path / '{}.json'.format(parent)
            with open(parent_json) as pjs:
                parent = lt.LanguageTree.from_json(pjs.read())
                this_meta = parent.meta
                this_meta.change_file_name = '{}.sc'.format(name)
    else:
        this_meta = meta

    cfp = this_data_path / this_meta.config_file_name
    scp = this_data_path / this_meta.change_file_name
    lxp = this_data_path / this_meta.lexicon_file_name
    cfp.touch()
    scp.touch()
    lxp.touch()
    node = lt.LanguageTree(meta=this_meta, name=name, date=date)
    return node


@plac.annotations(
    path=('The directory to initialize the project in.'),
    existing=('Allow initializing in an existing directory', 'flag', 'e'))
def init(name, path=None, existing=False):
    "Initialize a new PyLaut project."

    if not path:
        path = name

    pp = pathlib.Path(path).resolve()
    if not pp.exists() or existing:
        pp.mkdir(exist_ok=True)
        os.chdir(pp)
        fp = pp / "{}.json".format(name)
        dp = pp / 'data'
        dp.mkdir(exist_ok=True)
        lt = _create_languagetree_node(name, 0, name, pp, pp / 'data')
        with open(fp, 'w') as jsonf:
            jsonf.write(lt.to_json())
        return ["Successfully initialized new language tree in {}".format(pp)]
    else:
        return [
            "Directory {} already exists!\nSpecify -e to initialize anyway."
        ]


@plac.annotations(
    parent=('The name of the parent node.'),
    name=('The name of the node to create.'),
    date=('The date at which the stage is considered to have begun.'),
    project_path=(
        'The path to the project folder (defaults to current directory).'))
def node(parent: str, name: str, date: int, project_path='.'):
    "Create a new child language under an existing one."
    pp = pathlib.Path(project_path).resolve()
    parent_path = pp / '{}.json'.format(parent)
    project_name = pp.name
    if not pp.exists():
        return [
            "Could not find project: {}.".format(project_name),
            " Did you forget to specify a project path?"
        ]
    child = _create_languagetree_node(
        name, date, project_name, project_path, parent=parent)
    cpath = pp / '{}.json'.format(name)
    with cpath.open('w') as cjs:
        cjs.write(child.to_json())

    return ["Added child node {} to node {}".format(name, parent)]


@plac.annotations(
    parent=('The name of the parent node.'),
    language=('The name of the node to simulate.'),
    date=('The date at which the stage is considered to have begun.'),
    project_path=(
        'The path to the project folder (defaults to current directory).'))
def simulate(parent: str, language: str, date=None, project_path='.'):
    "Simulate the sound changes defined for a certain language."
    pp = pathlib.Path(project_path).resolve()
    project_name = pp.name
    if not pp.exists():
        return [
            "Could not find project: {}.".format(project_name),
            " Did you forget to specify a project path?"
        ]
    parent_path = pp / '{}.json'.format(parent)
    language_path = pp / '{}.json'.format(language)
    with parent_path.open() as pjs:
        parent_tree = lt.LanguageTree.from_json(pjs.read())
    with language_path.open() as ljs:
        language_tree = lt.LanguageTree.from_json(ljs.read())

    scp = pathlib.Path(
        language_tree.meta.data_path) / language_tree.meta.change_file_name
    lexp = pathlib.Path(
        parent_tree.meta.data_path) / parent_tree.meta.lexicon_file_name
    new_lexp = pathlib.Path(
        language_tree.meta.data_path) / language_tree.meta.lexicon_file_name
    with lexp.open() as lexf:
        lex = lexf.read()
    with scp.open() as scf:
        sc = scf.read()
    changes = parser.compile(sc)
    words = []
    new_words = []
    for line in lex:
        if line.startswith('#'):
            continue
        else:
            word = line.split()
            words.append(word)
    for word in words:
        for ch in changes:
            word[0] = ch.apply(word[0])
        new_words.append(word)
    with new_lexp.open() as nlf:
        strw = [str(word) for word in new_words]
        nlf.write("\n".join(strw))

    return ['Simulation successful.']


def __exit__(etype, exc, tb):
    "Will be called automatically at the end of the intepreter loop"
    if etype in (None, GeneratorExit):  # success
        print('ok')


def __missing__(name):
    return "Command {} does not exist! Perhaps you meant 'pylaut {}'?".format(
        name, _hamming_candidate(name, commands))


plac_main = __import__(__name__)


def main():
    for out in plac.call(plac_main, version='0.1.0'):
        print(out)


if __name__ == '__main__':
    main()
