from typing import get_origin, get_args
from types  import UnionType, GenericAlias


def check_type(obj:object, typ:type) -> bool:
    """
    check_type(obj:object, typ:type) -> bool:


    Checks if `obj` has type `type`. Returns True if the type of `obj` is `typ`
    -- if `typ` is a Generic type, then check if the type of `obj` is contained
    in the Union or origin of `typ`. Returns False otherwise.

    Note: Only some types of `obj` are checked for correct generic type
    parameters (c.f. the note in `check_generic_alias_type` for list of
    supported collection types).
    """

    if type(typ) == UnionType:
        # coerce type for mypy
        assert isinstance(typ, UnionType)
        return check_union_type(obj, typ)

    if type(typ) == GenericAlias:
        # coerce type for mypy
        assert isinstance(typ, GenericAlias)
        return check_generic_alias_type(obj, typ)
    
    return isinstance(obj, typ)


def check_generic_alias_type(obj:object, gtyp:GenericAlias) -> bool:
    """
    check_generic_alias_type(obj:object, gtyp:GenericAlias) -> bool:


    Checks if `obj` has type `gtype`. Returns True if the outer and inner
    types of `obj` corresponds to the generic type definition. E.g. to check
    if `obj` has type `list[int]` then return True only if `obj` is of type
    `list` and ALL elements are of type `int`. 

    Returns False for any nonsensical type definitions -- eg.:
    `dict[int, int, int]` or `list[int, str]`.

    Note: Only the `dict`, `list`, `tuple` datatypes are supported at the
    moment.
    """

    outer = get_origin(gtyp)
    inner = get_args(gtyp)

    if not check_type(obj, outer):
        return False

    # Trye some collectons -- this is not exhaustive, add more here if
    # necessary. Default to checking outer type only

    if outer == dict:
        # Dicts can have no type args => we're done
        if len(inner) == 0:
            return True
        # If the dict has type args, then it takes excactly two
        if len(inner) != 2:
            return False
        # Nwe that we have excatly two args, we can check that the key, value
        # pairs each have the correct type for each element of the dict
        key_type = inner[0]
        val_type = inner[1]
        for k, v in obj.items():
            if not check_type(k, key_type):
                return False
            if not check_type(v, val_type):
                return False
        # We're done with the dict type
        return True

    if outer == list:
        # Lists can have no type args => we're done
        if len(inner) == 0:
            return True
        # How are you supposed to read something like `list[int, float]`?
        if len(inner) > 1:
            return False
        # We have a well-defined element type => check each element of the list
        for elt in obj:
            if not check_type(elt, inner[0]):
                return False
        # We're done with the list type
        return True

    if outer == tuple:
        # Lists can have no type args => we're done
        if len(inner) == 0:
            return True
        # Tuples can either have no arguments, two arguments (with an ellipsis)
        # or a number of arguments equal to the number of elements
        if inner[-1] == Ellipsis:
            if len(inner) != 2:
                return False
            elt_type = inner[0]
            for elt in obj:
                if not check_type(elt, elt_type):
                    return False
            # We're done with the variable length tuple:
            return False
        # We've got a fix-length tuple
        if len(inner) != len(obj):
            return False
        # Check that each element in the tuple corresponds to the type list
        for i, elt in enumerate(obj):
            if not check_type(elt, inner[i]):
                return False
        # We're done with tuples
        return True

    # We're done with all the data types covered so far: out types match => OK
    return True


def check_union_type(obj:object, utyp:UnionType) -> bool:
    """
    check_union_type(obj:object, utyp:UnionType) -> bool:


    Checks if the type of `obj` is contained within the types of `utype`.
    Returns True on the first match.
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
        namespace['__post_init__'] = ValidatedDataClass.post_init
        return type.__new__(cls, name, bases, namespace)

    
    @staticmethod
    def post_init(self):
        """
        @staticmethod
        post_init(self):


        Raises TypeError if any of the fields in the the dataclass have a type
        different from their annotation
        """
        for (name, field_type) in self.__annotations__.items():
            if not check_type(self.__dict__[name], field_type):
                current_type = type(self.__dict__[name])
                raise TypeError(f"`{name}` is not a `{field_type}`")
