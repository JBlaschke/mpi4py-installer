from .validated_dataclasses import ValidatedDataClass

import sys

from dataclasses import dataclass


@dataclass(frozen=True)
class MPIConfig(metaclass=ValidatedDataClass):

    MPICC:   str|None = None
    CC:      str|None = None
    CFLAGS:  str|None = None
    LDFLAGS: str|None = None

    sys_prefix: str|list[str]|None = None
    init:       str|list[str]|None = None


    def __post_init__(self):
        if isinstance(self.sys_prefix, list):
            if not self.sys_prefix: # empty list
                object.__setattr__(self, "sys_prefix", None)

        if isinstance(self.init, list):
            if not self.init: # empty list
                object.__setattr__(self, "init", None)


    @staticmethod
    def check_prefix(prefix):
        return sys.prefix.startswith(prefix)


    @property
    def is_system_prefix(self) -> bool:
        """
        is_system_prefix -> bool

        Returns True only if the currently running interpreter's path starts
        with a string contained in MPIConfig.sys_prefix
        """

        if self.sys_prefix is None:
            return False

        if isinstance(self.sys_prefix, str):
            return MPIConfig.check_prefix(self.sys_prefix)

        # only remaining type for self.sys_prefix => list[str]
        for prefix in self.sys_prefix:
            if MPIConfig.check_prefix(prefix):
                return True

        return False
