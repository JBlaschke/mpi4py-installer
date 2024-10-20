import subprocess
import ctypes
import json
import re

from .. import load_site, load_user_site, logger, makecls,\
    Singleton, MPIConfig, ValidatedDataClass

from os              import environ, fsdecode
from sys             import platform
from types           import ModuleType
from pathlib         import Path
from dataclasses     import dataclass, field
from collections.abc import KeysView


@dataclass(frozen=True)
class Site(metaclass=makecls(Singleton, ValidatedDataClass)): # type: ignore
    """
    class Site(metaclass=Singleton):
        path
        user_path
        sites
        user_sites


    Stores site and user site path information. The user site is given by the
    MPI4PY_INSTALLER_SITE_CONFIG environment variable. Site is a global
    singleton: the paths are resolved once, and then retrieved from global
    memory on subsequent calls to the constructor.
    """

    path: Path = Path(__file__).parent.resolve()
    user_path: Path = Path(
        environ.get("MPI4PY_INSTALLER_SITE_CONFIG", default="~/.mpi4py")
    ).expanduser().resolve()
    sites: list[str] = field(init=False)
    user_sites: list[str] = field(init=False)


    def __post_init__(self):
        """
        __post_init__(self)


        Populates the list of valid site names. These are determiend by looking
        at the current directory, and the directory at
        `MPI4PY_INSTALLER_SITE_CONFIG`, then by enumerating all non-dunder .py
        files.
        """

        logger.debug("Searching for site definitions ...")

        def append_site(site_list: list[str], site: Path):
            if site.name.startswith("__") and site.name.endswith("__.py"):
                return
            site_list.append(site.stem)

        object.__setattr__(self, "sites", list())
        object.__setattr__(self, "user_sites", list())

        logger.debug(f"Searching {self.path=}")
        for x in self.path.glob("*.py"):
            append_site(self.sites, x)

        if self.user_path.is_dir():
            logger.debug(f"Searching {self.user_path=}")

            for x in self.user_path.glob("*.py"):
                append_site(self.user_sites, x)

        logger.debug(f"Found: {self.sites=}, {self.user_sites}")


def auto_site() -> tuple[str|None, bool]:
    """
    auto_site() -> tuple[str|None, bool]


    Check each of the sites if it's `check_site` returns `True`. 
    * If one site's `check_site` returns `True` return that site's name.
    * If more than one site's `check_site` returns `true` then return `None`

    Returns: (auto-dected site name, flag)
    * flag is `True` only if the returned site name is a user-defined site
    """

    logger.debug("Searching for compatible sites")

    site_info = Site()

    found = None
    for s in site_info.sites:
        site = load_site(s)
        if (found is None) and site.check_site():
            logger.debug(f"Found: site={s}")
            found = s
        elif (found is not None) and site.check_site():
            logger.debug(f"Found second site candidate: {s}")
            logger.critical("Warning multiple compatible sites detected!")
            return None, False

    flag = False
    for s in site_info.user_sites:
        site = load_user_site(s, site_info.user_path)
        if (found is None) and site.check_site():
            logger.debug(f"Found: site={s}")
            found = s
            flag  = True
        elif (found is not None) and site.check_site():
            logger.debug(f"Found second site candidate: {s}")
            logger.critical("Warning multiple compatible sites detected!")
            return None, False

    return found, flag


@dataclass(frozen=True)
class ConfigEnv(metaclass=ValidatedDataClass):
    """
    @dataclass(frozen=True)
    class ConfigEnv(metaclass=ValidatedDataClass):
        _env: dict[str, str|list[str]]


    Storage class for environment configuration -- use `__getitem__` to access
    `_env`; and `keys` to get a list of defined keys in `_env`.
    """
    _env: dict[str, str|list[str]]


    def __post_validate__(self):
        assert "host" in self._env.keys()
        assert "blacklist" in self._env.keys()


    def __getitem__(self, key) -> str|list[str]:
        return self._env[key]


    def keys(self) -> KeysView:
        return self._env.keys()


    @property
    def host(self) -> str:
        # type narrowing for mypy
        assert isinstance(self["host"], str)
        return self["host"]


@dataclass(frozen=True)
class ConfigSys(metaclass=ValidatedDataClass):
    """
    @dataclass(frozen=True)
    class ConfigSys(metaclass=ValidatedDataClass):
        _sys: dict[str, MPIConfig]


    Storage class for system configuration -- use `__getitem__` to access
    `_sys`; and `keys` to get a list of defined keys in `_sys`. Each key is a
    build vaiant on the system.
    """
    _sys: dict[str, MPIConfig]


    def __getitem__(self, key) -> MPIConfig:
        return self._sys[key]


    def keys(self) -> KeysView:
        return self._sys.keys()


@dataclass(frozen=True)
class ConfigStore(metaclass=makecls(Singleton, ValidatedDataClass)): # type: ignore
    file: str

    _valid: bool = field(init=False)

    config_file: Path = field(init=False)

    env:           ConfigEnv  = field(init=False)
    sys: dict[str, ConfigSys] = field(init=False)


    def __post_init__(self):
        """
        __post_init__(self)


        Load any data contained in the json file with the same file name as
        `self.file`. E.g. `/path/to/module.py` will attempt to load
        `/path/to/module.json`. If the json file could not be loaded,
        `self.valid` is set to False, and `self.data` is set to None
        """

        module_path = Path(self.file).resolve()
        config_file = module_path.parent / Path(module_path.stem + ".json")
        env_config, sys_config = ConfigStore.load_config_file(config_file)

        object.__setattr__(
            self, "_valid",
            (env_config is not None) and (sys_config is not None)
        )
        object.__setattr__(self, "config_file", config_file)

        if self._valid:
            # narrow mypy data type
            assert env_config is not None
            assert sys_config is not None

            object.__setattr__(self, "env", ConfigEnv(_env = env_config))
            object.__setattr__(self, "sys", dict())

            for system in sys_config.keys():
                self.sys[system] = ConfigSys(_sys = {
                    variant: MPIConfig(**var_config) # type: ignore
                    for variant, var_config in sys_config[system].items()
                })


    @property
    def valid(self) -> bool:
        """
        valid -> bool


        Data contained within represents a loaded MPI configuration. If `False`
        then this ConfigStore does not contain any loaded MPI configurations.
        """
        return self._valid


    @property
    def systems(self) -> list[str]:
        """
        systems -> list[str]


        List of all systems contained in this config
        """
        return [system for system in self.sys.keys()]


    def variants(self, system: str) -> list[str]:
        """
        def variants(self, system: str) -> list[str]:


        List of all variants on this site for a given system
        """
        return [variant for variant in self.sys[system].keys()]


    @staticmethod
    def load_config_file(config_file_path: Path) -> tuple[
                dict[str, str | list[str]] | None,
                dict[str, dict[str, dict[str, str | list[str] | None ]]] | None
            ]:
        """
        load_config_file(config_file_path: Path) -> tuple[
                dict[str, str | list[str]] | None,
                dict[str, dict[str, dict[str, str | list[str] | None ]]] | None
            ]

        Load a json at the location of `config_file_path`. Does some basic
        validation (file is a json file, file exists). The contents of the json
        object are not validated.

        * If the config file does not exist, or if it's not a json file, then
          return None
        """

        if not config_file_path.is_file():
            logger.critical(f"File {config_file_path=} does not exist")
            return None, None

        if config_file_path.suffix != ".json":
            logger.critical(
                f"Cannot load config file at {config_file_path=} -- not a json"
            )
            return None, None

        with open(config_file_path, "r") as f:
            data = json.load(f)

        if "environment" not in data.keys():
            logger.critical(
                f"'environment' is not a root key of {config_file_path}"
            )
            return None, None


        if "systems" not in data.keys():
            logger.critical(
                f"'systems' is not a root key of {config_file_path}"
            )
            return None, None

        return data["environment"], data["systems"]


def default_check_site(config: ConfigStore) -> bool:
    logger.debug("Using default check_site")

    host_varname   = config.env["host"]
    blacklist_vars = config.env["blacklist"]

    logger.debug(f"{host_varname=}, {blacklist_vars=}")

    is_site = host_varname in environ
    if is_site:
        if any(blv in environ for blv in blacklist_vars):
            is_site = False

    logger.debug(f"{is_site=}")
    return is_site


def default_available_systems(config: ConfigStore) -> list[str]:
    logger.debug("Using default available_systems")
    return config.systems


def default_determine_system(config: ConfigStore) -> str:
    logger.debug("Using default determine_system")

    host_varname = config.env.host

    logger.debug(f"{host_varname=}, {config.systems=}")

    if host_varname not in environ:
        logger.warning(
            f"{host_varname=} is not in environment. Defaulting to 'default'"
        )
        host_name = "default"
    else:
        host_name = environ[host_varname]

    if host_name not in config.systems:
        logger.critical(
            f"No section for '{host_name}' exists in: {config.config_file}"
        )
        raise RuntimeError(f"Could not find settings for system '{host_name}'")
    assert host_name in config.systems

    logger.debug(f"{host_name=}")
    return host_name


def default_available_variants(config: ConfigStore, system: str) -> list[str]:
    logger.debug("Using default available_variants")

    if system not in config.systems:
        logger.critical(
            f"No section for '{system}' exists in: {config.config_file}"
        )
        raise RuntimeError(f"Could not find settings for system '{system}'")

    return config.variants(system)


def default_config(
            config: ConfigStore, system: str, variant: str
        ) -> MPIConfig:
    logger.debug(f"Using default config for {system=}, {variant=}")

    if system not in config.systems:
        logger.critical(
            f"No section for '{system}' exists in: {config.config_file}"
        )
        raise RuntimeError(f"Could not find settings for system '{system}'")

    if variant not in config.variants(system):
        logger.critical(
            f"No section for '{variant}' for system '{system}'"
        )
        raise RuntimeError(f"Could not find settings for variant '{variant}'")

    return config.sys[system][variant]


def get_mpicc_link_data(config: MPIConfig) -> tuple[list[str], list[str]]|None:
    try:
        # Run the mpicc command to show the underlying compiler command
        output = subprocess.run(
            [config.MPICC, config.mpicc_show],
            capture_output=True, text=True, check=True
        ).stdout

        # Print the output for debugging purposes
        logger.debug(f"{config.MPICC} {config.mpicc_show} output: {output}")

        # Regular expression to match library paths (e.g., -L/path/to/lib and -lmpi)
        lib_path_pattern = re.compile(r'-L(\S+)')
        lib_name_pattern = re.compile(r'-l(\S+)')

        # Find all library paths and names
        lib_paths = lib_path_pattern.findall(output)
        lib_names = lib_name_pattern.findall(output)

        # Print the found paths and names
        logger.debug(f"{config.MPICC} library paths: {lib_paths}")
        logger.debug(f"{config.MPICC} linked libraries: {lib_names}")

        return lib_paths, lib_names

    except subprocess.CalledProcessError as e:
        logger.critical("Failed to run mpicc command")
        return None


def get_mpi_library_path(MPI_module: ModuleType) -> str | None:
    if platform.startswith("linux") or platform == "darwin":
        # Linux and macOS
        class DL_Info(ctypes.Structure):
            _fields_ = [
                ("dli_fname", ctypes.c_char_p),
                ("dli_fbase", ctypes.c_void_p),
                ("dli_sname", ctypes.c_char_p),
                ("dli_saddr", ctypes.c_void_p),
            ]

        libc = ctypes.CDLL(None)
        dladdr = libc.dladdr
        dladdr.restype = ctypes.c_int
        dladdr.argtypes = [ctypes.c_void_p, ctypes.POINTER(DL_Info)]

        module = ctypes.CDLL(MPI_module.__file__)
        symbol = module.MPI_Init
        dl_info = DL_Info()
        result = dladdr(
            ctypes.cast(symbol, ctypes.c_void_p), ctypes.byref(dl_info)
        )

        if result == 0:
            logger.critical("dladdr call failed")
            return None

        libmpi = fsdecode(dl_info.dli_fname)
        return libmpi

    elif platform == "win32":
        # Windows
        module = ctypes.windll.LoadLibrary(MPI_module.__file__)
        buffer = ctypes.create_unicode_buffer(260)
        GetModuleFileName = ctypes.windll.kernel32.GetModuleFileNameW
        GetModuleFileName.argtypes = [
            ctypes.wintypes.HMODULE,
            ctypes.wintypes.LPWSTR,
            ctypes.wintypes.DWORD
        ]
        GetModuleFileName.restype = ctypes.wintypes.DWORD

        result = GetModuleFileName(
            module._handle, buffer, ctypes.sizeof(buffer)
        )

        if result == 0:
            logger.critical("GetModuleFileName call failed")
            return None

        libmpi = buffer.value
        return libmpi

    else:
        logger.critical(f"Unsupported platform: {platform}")
        return None
