# Chache storing generated metaclasses -- each metaclass generated by
# __generate_metaclass is stored here along with its bases.
METADICT = dict()


def __generate_metaclass(bases, metas, priority):
    # hackish!! m is trivial if it is 'type' or, in the case explicit
    # metaclasses are given, if it is a superclass of at least one of them
    trivial   = lambda m: sum([issubclass(M, m) for M in metas],m is type)
    metabs    = tuple([mb for mb in map(type, bases) if not trivial(mb)])
    metabases = (metabs + metas, metas + metabs)[priority]

    # already generated metaclass => return chacked metaclass
    if metabases in METADICT:
        return METADICT[metabases]

    # trivial metabase: the type object. This doesn't need to be cached.
    if not metabases:
        return type

    # if there is only one metabase, then no need to generate a new metaclass.
    # This also doesn't need to be cached.
    if len(metabases) == 1:
        return metabases[0]

    # name of the new metaclass representing the metabases
    metaname = "__" + "_".join([m.__name__ for m in metabases])
    meta     = makecls()(metaname, metabases, {})

    return METADICT.setdefault(metabases, meta)


def makecls(*metas, **options):
    """
    makecls(*metas, **options):


    Class factory avoiding metatype conflicts. The invocation syntax is:
    ```
    makecls(M1, M2, .., priority=1)(name, bases, dict)
    ```
    If the base classes have metaclasses conflicting within themselves or with
    the given metaclasses, it automatically generates a compatible metaclass
    and instantiate it. If priority is True, the given metaclasses have
    priority over the bases' metaclasses
    """

    priority = options.get("priority", 0) # default, no priority
    return lambda n,b,d: __generate_metaclass(b, metas, priority)(n, b, d) 