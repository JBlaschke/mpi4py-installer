from .. import logger
from os import environ
from importlib.machinery import SourceFileLoader


def check_site() -> bool:
    return "MPI4PY_LOCAL" in environ


def determine_system() -> str:
    return "local"


def available_variants(system: str) -> list[str]:
    return ["default", "site:<site_variant>"]


def auto_variant(system: str) -> str:
    return "default"


def config(system: str, variant: str) -> dict[str, str]:
    config = dict()

    if variant == "default":
        config["sys_prefix"] = "None"
        config["MPICC"] = "mpicc"
    elif variant.startswith("site:"):
        site_config = SourceFileLoader(
            "local_site_config", environ["MPI4PY_LOCAL"]
        ).load_module()
        return site_config.config(variant)
    else:
        raise RuntimeError(f"Unknown {variant=}")

    return config


def init(system: str, variant: str) -> str:
    if variant == "default":
        return ""
    elif variant.startswith("site:"):
        site_config = SourceFileLoader(
            "local_site_config", environ["MPI4PY_LOCAL"]
        ).load_module()
        return site_config.init(variant)
    else:
        raise RuntimeError(f"Unknown {variant=}")


def sanity(system: str, variant: str, config: dict[str, str]) -> bool:
    logger.debug(f"{system=}, {variant=}, {config=}")

    import mpi4py
    mpi4py_config = mpi4py.get_config()
    logger.debug(f"Sanity: {mpi4py_config=}")
    return mpi4py_config['mpicc'].endswith(config["MPICC"])