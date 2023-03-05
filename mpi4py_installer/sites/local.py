from .. import logger
from os import environ
from importlib.machinery import SourceFileLoader


def check_site() -> bool:
    return "MPI4PY_LOCAL" in environ


def determine_system() -> str:
    host = environ.get("MPI4PY_HOST", default="default:default")
    host, _ = host.split(":")
    return host


def available_variants(system: str) -> list[str]:
    host = environ.get("MPI4PY_HOST", default="default:default")
    _, variants = host.split(":")
    return variants.split(",")


def auto_variant(system: str) -> str:
    logger.debug(f"{system=}")
    variants = available_variants(system)
    return variants[0]


def config(system: str, variant: str) -> dict[str, str]:
    logger.debug(f"{system=}, {variant=}")

    config = dict()
    if system == "default":
        config["sys_prefix"] = "None"
        config["MPICC"] = "mpicc"
    else:
        site_config = SourceFileLoader(
            "local_site_config", environ["MPI4PY_LOCAL"]
        ).load_module()
        return site_config.config(variant)

    return config


def init(system: str, variant: str) -> str:
    logger.debug(f"{system=}, {variant=}")

    if system == "default":
        return ""
    else:
        site_config = SourceFileLoader(
            "local_site_config", environ["MPI4PY_LOCAL"]
        ).load_module()
        return site_config.init(variant)


def sanity(system: str, variant: str, config: dict[str, str]) -> bool:
    logger.debug(f"{system=}, {variant=}, {config=}")

    import mpi4py
    mpi4py_config = mpi4py.get_config()
    logger.debug(f"Sanity: {mpi4py_config=}")
    return mpi4py_config['mpicc'].endswith(config["MPICC"])