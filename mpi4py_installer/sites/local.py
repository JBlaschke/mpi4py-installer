from .  import ConfigStore, MPIConfig, \
    default_check_site, default_available_systems, default_determine_system, \
    default_available_variants, default_config, get_mpi_library_path, \
    get_mpicc_link_data
from .. import logger

from os      import environ
from pathlib import Path


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
    # Default to returning `None` is there is no init data
    return None


def sanity(system: str, variant: str, config: MPIConfig) -> bool:
    logger.debug(f"{system=}, {variant=}, {config=}")

    # Extract the path of the underlying MPI library``
    import mpi4py
    mpi4py.rc.initialize = False
    from mpi4py import MPI
    mpi_lib_path = get_mpi_library_path(MPI)
    logger.info(f"The MPI library path is: {mpi_lib_path}")

    # Extract all paths from the mpicc linker
    mpicc_lib_dirs, mpicc_libs = get_mpicc_link_data(config)
    logger.info(f"The {config.MPICC} {config.mpicc_show} libraries are:")
    logger.info(f"{mpicc_lib_dirs=}")
    logger.info(f"{mpicc_libs=}")

    # Going through all possible combinations of lib_dir/lib_name. Use the
    # `resolve` function to resolve symlinks -- we'll always compare the "real"
    # paths.
    target = Path(mpi_lib_path).resolve()
    for dir in mpicc_lib_dirs:
        for lib in mpicc_libs:
            f = Path(dir) / ("lib" + lib + ".so")
            f = f.resolve()
            logger.debug(f"Checking: {f}")
            if f == target:
                return True

    # Clearly no matches found => the MPI library used by mpi4py (as resolved
    # by the linker) is NOT any of the libraries linked against by MPICC
    return False

