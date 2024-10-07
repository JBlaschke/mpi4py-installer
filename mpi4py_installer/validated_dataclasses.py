from typing import get_origin, get_args
from types  import UnionType


def check_type(obj:object, typ:type) -> bool:
    """
    check_type(obj:object, typ:type) -> bool:


    Checks if `obj` has type `type`. Returns True if the type of `obj` is `typ`
    -- if `typ` is a Generic type, then check if the type of `obj` is contained
    in the Union or origin of `typ`. Returns False otherwise.

    Note: Does not check if `obj` is of the correct generic type (this would be
    hard for any collection types anyway).
    """

    if get_origin(typ) == UnionType:
        return check_union_type(obj, typ)

    return check_singular_type(obj, typ)


def check_singular_type(obj:object, styp:type) -> bool:
    """
    check_singular_type(obj:object, styp:type) -> bool:


    Checks if `obj` has type `stype`. The target `stype` needs to be a regular
    (non-generic) type, or a generic type but not a UnionType. Does not check
    if `obj` is of the correct generic type (this would be hard for any
    collection types anyway).
    """

    if get_args(styp) == ():
        return isinstance(obj, styp)

    return check_type(obj, get_origin(styp))


def check_union_type(obj:object, utyp:UnionType) -> bool:
    """
    check_union_type(obj:object, utyp:UnionType) -> bool:


    Checks if the type of `obj` is contained within the types of `utype`.
    Returns True on the first match. Does not check if `obj` is of the correct
    generic type (this would be hard for any collection types anyway).
    """

    for typ in get_args(utyp):
        if check_type(obj, typ):
            return True

    return False


class ValidatedDataClass(type):
    """
    ValidatedDataClass


    A metaclass that will define a __post_init__ method which will check that
    the types of all attributes match the type annotations. If used together
    with @dataclass, then __post_init__ is called automatically.

    Recommended use is:

    @dataclass(frozen=True)
    class MyData:
        ...

    as this will ensure that `MyData's` attributes will have the correct types,
    (and immutability will ensure that these won't change during runtime)
    """

    def __new__(cls, name, bases, namespace):
        namespace['__post_init__'] = cls.post_init
        return type.__new__(cls, name, bases, namespace)


    def post_init(self):
        """
        post_init(self):


        Raises TypeError if any of the fields in the the dataclass have a type
        different from their annotation
        """
        for (name, field_type) in self.__annotations__.items():
            if not check_type(self.__dict__[name], field_type):
                current_type = type(self.__dict__[name])
                raise TypeError(
                    f"`{name}` is not a `{field_type}` [got: `{current_type}`]"
                )
