import json

from ..          import load_site, load_user_site, logger, Singleton, MPIConfig
from os          import environ
from pathlib     import Path
from dataclasses import dataclass, field


@dataclass
class Site(metaclass=Singleton):
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

        self.sites: list[str] = list()
        self.user_sites: list[str] = list()

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


CONFIG_DICT = dict[str, str|list[str]|dict[str, str]]

@dataclass
class ConfigEnv():
    pass


@dataclass
class ConfigStore(metaclass=Singleton):
    file: str
    data: CONFIG_DICT|None = field(init=False)

    config_file: Path = field(init=False)
    config_valid: bool = field(init=False)

    config_env: dict[str, str|list[str]] = field(init=False)
    config_sys: dict[str, dict[str,str]] = field(init=False)


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
        self.data = ConfigStore.load_config_file(config_file)
        self.config_file = config_file


    @property
    def valid(self) -> bool:
        """
        valid -> bool


        Data set is valid for processing
        """
        return self.data is not None


    @property
    def systems(self) -> list[str]|None:
        """
        systems -> list[str]|None


        List of all systems contained in this config
        """
        assert self.data is not None
        return site_systems(self.data)


    def variants(self, system: str) -> list[str]:
        """
        def variants(self, system: str) -> list[str]:


        List of all variants on this site for a given system
        """
        assert self.data is not None
        return system_variants(self.data, system)


    @staticmethod
    def load_config_file(config_file_path: Path) -> CONFIG_DICT|None:
        """
        CONFIG_DICT = dict[str, str|list[str]|dict[str, str]]
        load_config_file(config_file_path: Path) -> CONFIG_DICT|None


        Load a json at the location of `config_file_path`. Does some basic
        validation (file is a json file, file exists). The contents of the json
        object are not validated.

        * If the config file does not exist, or if it's not a json file, then
          return None
        """

        if not config_file_path.is_file():
            logger.critical(f"File {config_file_path=} does not exist")
            return None

        if config_file_path.suffix != ".json":
            logger.critical(
                f"Cannot load config file at {config_file_path=} -- not a json"
            )
            return None

        with open(config_file_path, "r") as f:
            data = json.load(f)

        return data


def site_systems(site_config: CONFIG_DICT) -> list[str]:
    """
    CONFIG_DICT = dict[str, str|list[str]|dict[str, str]]
    site_systems(site_config: CONFIG_DICT) -> list[str]


    Return a list of available sites descirbed in the config dictionary
    """

    return [k for k in site_config.keys() if not k.startswith("__")]


def system_variants(site_config: CONFIG_DICT, system: str) -> list[str]:
    """
    CONFIG_DICT = dict[str, str|list[str]|dict[str, str]]
    system_variants(site_config: CONFIG_DICT, system: str) -> list[str]


    Return a list of valiable variants descirbed in the config dictionary for
    the specified system
    """
    system_config = site_config[system]
    assert isinstance(system_config, dict)
    return [k for k in system_config.keys()]


def default_check_site(config: ConfigStore) -> str:
    logger.debug("Using default check_site")

    env_descriptor = config.data["__environment"]
    host_varname   = env_descriptor["host"]
    blacklist_vars = env_descriptor["blacklist"]

    logger.debug(f"{host_varname=}, {blacklist_vars=}")

    is_site = host_varname in environ
    if is_site:
        if any(blv in environ for blv in blacklist_vars):
            is_site = False

    logger.debug(f"{is_site=}")
    return is_site


def default_determine_system(config: ConfigStore) -> str:
    logger.debug("Using default determine_system")

    env_descriptor = config.data["__environment"]
    host_varname   = env_descriptor["host"]

    logger.debug(f"{host_varname=}, {config.systems=}")

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
        ) -> dict[str, str]:
    logger.debug(f"Using default config for {system=}, {variant=}")

    if system not in config.systems:
        logger.critical(
            f"No section for '{system}' exists in: {config.config_file}"
        )
        raise RuntimeError(f"Could not find settings for system '{system}'")

    if variant not in config.variants(system):
        logger.critical(
            f"No section for '{variants}' for system '{system}'"
        )
        raise RuntimeError(f"Could not find settings for variant '{variant}'")

    return MPIConfig(**config.data[system][variant])
