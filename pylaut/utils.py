from collections.abc import Iterable
from copy import deepcopy
import itertools
import pdb
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

def split(iterable, sep=" "):
    if isinstance(iterable, str):
        return iterable.split(sep)
    slices = []
    current_slice = []
    for elem in iterable:
        if elem == sep:
            slices.append(current_slice)
            current_slice = []
        else:
            current_slice.append(elem)
    slices.append(current_slice)
    return slices

def replace(iterable, target, *args):
    if isinstance(iterable, str):
        return iterable.replace(target, "".join(args))
    else:
        new_iterable = []
        for elem in iterable:
            if elem == target:
                new_iterable.append(elem)
                for a in args:
                    new_iterable.append(a)
            new_iterable.append(elem)
        return new_iterable


class EmptyException(Exception):
    """
    An exception raised when a value or attribute necessary for some operation
    is empty or None.
    """
    pass
