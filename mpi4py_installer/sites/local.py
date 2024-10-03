from .  import ConfigStore, default_check_site, default_determine_system, \
    default_available_variants, default_config
from .. import logger
from os import environ


# Loads __file__.json
CONFIG = ConfigStore(__file__)


def check_site() -> bool:
    return default_check_site(CONFIG)


def determine_system() -> str:
    return default_determine_system(CONFIG)


def available_variants(system: str) -> list[str]:
    return default_available_variants(CONFIG, system)


def auto_variant(system: str) -> str:
    variants = default_available_variants(system)
    return variants[0]


def config(system: str, variant: str) -> dict[str, str]:
    return default_config(CONFIG, system, variant)


def init(system: str, variant: str) -> str:  # TODO: init should able to return `None`
    logger.debug(f"{system=}, {variant=}")
    config = default_config(CONFIG, system, variant)
    return config["init"]


def sanity(system: str, variant: str, config: dict[str, str]) -> bool:
    logger.debug(f"{system=}, {variant=}, {config=}")

    import mpi4py
    mpi4py_config = mpi4py.get_config()
    logger.debug(f"Sanity: {mpi4py_config=}")
    return mpi4py_config['mpicc'].endswith(config["MPICC"])
