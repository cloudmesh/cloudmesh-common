import pydoc

c = pydoc.locate("cloudmesh")

print(dir(c))
print(c.__package__)
print()
print(c.__spec__)

print()
print(c.__path__)
print(c.__name__)
print(c.__loader__)
print(c.__file__)
print(c.__cached__)

print()
print('\n'.join(c.__path__))


def inheritors(klass):
    """
    returns the inheritors of a class if it is loaded

    :return: a set of classes
    """
    subclasses = set()
    work = [klass]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return subclasses


d = pydoc.locate("cloudmesh.abstract.ComputeNodeABC")

print(inheritors(d))


def get_all_subclasses(cls):
    all_subclasses = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))

    return all_subclasses


print(dir(c))
