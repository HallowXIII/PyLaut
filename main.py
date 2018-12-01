"""
A CLI interface to the PyLaut APIs.
"""

import plac
import os
import pathlib

from pylaut.change import languagetree as lt

commands = ["init", "node"]


def _hamming_candidate():
    pass


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
    else:
        this_meta = meta

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
            jsonf.write(lt.json())
        return ["Successfully initialized new language tree in {}".format(pp)]
    else:
        return [
            "Directory {} already exists!\nSpecify -e to initialize anyway."
        ]


@plac.annotations()
def node(parent: str, name: str, date: int, project_path='.'):
    "Create a new child language under an existing one."
    pp = pathlib.Path(project_path).resolve()
    parent_path = pp / '{}.json'.format(parent)
    if not pp.exists():
        return [
            "Could not find project: {}.",
            " Did you forget to specify a project path?"
        ]
    with parent_path.open() as pjs:
        parent = lt.LanguageTree.from_json(pjs.read())
    project_name = project_path.name()
    child = _create_languagetree_node(
        name, date, project_name, project_path, parent=parent)
    cpath = pp / '{}.json'.format(name)
    with cpath.open('w') as cjs:
        cjs.write(child.json())

    return ["Added child node {} to node {}".format(name, parent.name)]


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
