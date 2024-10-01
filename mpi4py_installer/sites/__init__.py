import json

from ..      import load_site, logger
from os      import environ
from pathlib import Path


# register new sites here
available_sites = [
    "local",
    "nersc"
]

def find_available_sites() -> tuple[list[str], list[str]]:
    """
    find_available_sites() -> list[str]


    Returns a list of valid site names. These are determiend by looking at the
    current directory, and the directory at `MPI4PY_INSTALLER_SITE_CONFIG`,
    then by enumerating all non-dunder .py files.
    """
    logger.debug("Searching for site definitions ...")

    def append_site(site_list: list[str], site: Path):
        if site.name.startswith("__") and site.name.endswith("__.py"):
            return
        site_list.append(site.stem)

    sites: list[str] = list()
    user_sites: list[str] = list()

    site_path = Path(__file__).parent.resolve()
    logger.debug(f"Searching {site_path=}")
    for x in site_path.glob("*.py"):
        append_site(sites, x)

    user_site_path = Path(
        environ.get("MPI4PY_INSTALLER_SITE_CONFIG", default="~/.mpi4py")
    ).resolve()
    if user_site_path.is_dir():
        logger.debug(f"Searching {user_site_path=}")

        for x in user_site_path.glob("*.py"):
            append_site(user_sites, x)

    logger.debug(f"Found: {sites=}, {user_sites}")
    return sites, user_sites


def auto_site() -> str|None:
    """
    auto_site() -> str


    Check each of the sites registered in `available_sites` if it's `check_site`
    returns true.

    * If one site's `check_site` returns `True` return that site's name.
    * If more than one site's `check_site` returns `true` then return `None`
    """
    logger.debug("Searching for compatible sites")

    found = None
    for s in available_sites:
        site = load_site(s)
        if (found is None) and site.check_site():
            logger.debug(f"Found: site={s}")
            found = s
        elif (found is not None) and site.check_site():
            logger.debug(f"Found second site candidate: {s}")
            logger.critical("Warning multiple compatible sites detected!")
            return None

    return found


def load_config_file(config_file_path: str) -> dict[str, str]:
    """
    load_config_file(config_file_path: str) -> dict[str, str]

    Load a json at the location of `config_file_path`. Does some basic
    validation (file is a json file, file exists). The contests of the json
    object are not validated.
    """
    path = Path(config_file_path)

    if not path.is_file():
        logger.critical(f"File {path=} does not exist")



    if path.suffix != ".json":
        logger.critical(f"Cannot load config file at {path=} -- not a json")
        return dict()

    with open(path, "r") as f:
        data = json.load(f)

    return data
