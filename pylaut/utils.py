from collections.abc import Iterable
from copy import deepcopy
import itertools

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

def change_feature(phone, name, value):
    np = deepcopy(phone)
    if value:
        np.set_features_true(name)
    else:
        np.set_features_false(name)
    np.set_symbol_from_features()
    return np

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
                
