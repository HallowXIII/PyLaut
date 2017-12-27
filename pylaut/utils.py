from collections.abc import Iterable
from copy import deepcopy
import itertools
from typing import Union, List, Generic, TypeVar, NewType

def breakat(ls, breaks):
    slices = []
    lastbrk = 0
    for brk in breaks:
        slices.append(ls[lastbrk:brk])
        lastbrk = brk
    slices.append(ls[lastbrk:])
    return slices

def powerset(iterable):
    s = list(iterable)
    return itertools.chain.from_iterable(
        itertools.combinations(s, r) for r in range(len(s)+1))

def forall(ls, pred):
    return all(map(pred, ls))

def exists(ls, pred):
    return any(map(pred, ls))

def mapwith(pred, fun, ls):
    return (fun(item) if pred(item) else item for item in ls)

def fand(f, g):
    return lambda x: f(x) and g(x)

def o(f, g):
    return lambda x: f(g(x))

def milchreis():
    return float("Infinity")

def flatten(ls):
    return [elem for subl in ls for elem in subl]

def flatten_partial(ls):
    new = []
    for item in ls:
        if isinstance(item, Iterable):
            for si in item:
                new.append(si)
        else:
            new.append(item)
    return new

class Stm(object):
    """
    Stm for 'statement'. This is a wrapper class to allow for
    things resembling statement block expressions. Sadly,
    most side-effecting functions in Python are methods, and
    dynamic method resolution would require use of 'eval',
    so most uses of this will still require a bunch of
    lambdas.
    """

    def __init__(self, istate):
        self.state = istate

    def __rshift__(self, vfunc):
        vfunc(self.state)
        return self

    def __call__(self):
        return self.state

class StmP(object):
    """
    Similar to the Stm class, but with persistence in the state.
    """

    def __init__(self, istate):
        self.state = istate

    def __rshift__(self, vfunc):
        newstate = deepcopy(self.state)
        vfunc(newstate)
        return Stm(newstate)

    def __call__(self):
        return self.state

def block(istate):
    """
    Simulates a statement block as an expression
    """
    def _block_(*args):
        return istate

    return _block_
