import sys

from dataclasses import dataclass


@dataclass
class MPIConfig:

    MPICC:   str|None = None
    CC:      str|None = None
    CFLAGS:  str|None = None
    LDFLAGS: str|None = None

    sys_prefix: str|list[str]|None = None

    def __post_init__(self):
        for (name, field_type) in self.__annotations__.items():
            if not isinstance(self.__dict__[name], field_type):
                current_type = type(self.__dict__[name])
                raise TypeError(
                    f"{name} is not a {field_type} (instead of {current_type})"
                )


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
