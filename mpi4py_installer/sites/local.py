from .  import ConfigStore, MPIConfig, \
    default_check_site, default_available_systems, default_determine_system, \
    default_available_variants, default_config
from .. import logger

from os import environ


# Loads __file__.json
CONFIG = ConfigStore(__file__)


def check_site() -> bool:
    return default_check_site(CONFIG)


def available_systems() -> list[str]:
    return default_available_systems(CONFIG)


def determine_system() -> str:
    return default_determine_system(CONFIG)


def available_variants(system: str) -> list[str]:
    return default_available_variants(CONFIG, system)


def auto_variant(system: str) -> str:
    variants = default_available_variants(CONFIG, system)
    return variants[0]


def config(system: str, variant: str) -> MPIConfig:
    return default_config(CONFIG, system, variant)


def init(system: str, variant: str) -> str|None:
    logger.debug(f"{system=}, {variant=}")
    config = default_config(CONFIG, system, variant)
    if config.init is not None:
        return "\n".join(config.init)
    # Defailt to returning `None` is there is no init data
    return None


def sanity(system: str, variant: str, config: MPIConfig) -> bool:
    logger.debug(f"{system=}, {variant=}, {config=}")

    if config.MPICC is None:
        # nothing to test here
        return True

    import mpi4py
    mpi4py_config = mpi4py.get_config()
    logger.debug(f"Sanity: {mpi4py_config=}")
    return mpi4py_config['mpicc'].endswith(config.MPICC)
