import hashlib
import json

from typing import Any


def dict_hash(dictionary: dict[str, Any]) -> str:
    """
    dict_hash(dictionary: dict[str, Any]) -> str

    MD5 hash of a dictionary. This is used to retrieve an existing class
    instance from the singleton `_instances` store. The dictionary is
    respresented by a json with sorted keys.
    """
    dhash = hashlib.md5()
    # We need to sort arguments so {'a': 1, 'b': 2} is
    # the same as {'b': 2, 'a': 1}
    encoded = json.dumps(dictionary, sort_keys=True).encode()
    dhash.update(encoded)
    return dhash.hexdigest()


class Singleton(type):
    """
    class MySingleton(metaclass=Singleton):
        ...

    Setting `metaclass=Singleton` in the classes meta descriptor marks it as a
    singleton object: if the object has already been constructed elsewhere in
    the code, subsequent calls to the constructor just return this original
    instance.
    """

    # Stores instances in a dictionary:
    # {class: instance}
    _instances: dict[Any, Any] = dict()

    def __call__(cls, *args, **kwargs):
        """
        Metclass __call__ operator is called before the class constructor -- so
        this operator will check if an instance already exists in
        Singleton._instances. If it doesn't call the constructor and add the
        instance to Singleton._instances. If it does, then don't call the
        constructor and return the instance instead.
        """

        hash = dict_hash({"args": args, "kwargs": kwargs})
        if (cls, hash) not in cls._instances:
            cls._instances[(cls, hash)] = super(Singleton, cls).__call__(
                *args, **kwargs
            )

        return cls._instances[(cls, hash)]
