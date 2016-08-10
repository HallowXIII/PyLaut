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
