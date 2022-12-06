from .. import logger
from os import environ


def check_site() -> bool:
    return "NERSC_HOST" in environ


def determine_system() -> str:
    return environ["NERSC_HOST"]


def available_variants(system: str) -> list[str]:
    if system == "perlmutter":
        return ["cpu:gnu", "gpu:gnu", "gpu:nvidia"]
    elif system == "cori":
        return ["gnu"]
    else:
        raise RuntimeError(f"Unknown {system=}")


def auto_variant(system: str) -> str:
    logger.debug(f"{system=}")
    if system == "perlmutter":
        return "gpu:gnu"
    elif system == "cori":
        return "gnu"
    else:
        raise RuntimeError(f"Unknown {system=}")


def config(system: str, variant: str) -> dict[str, str]:
    logger.debug(f"{system=}, {variant=}")

    config = {"sys_prefix": "/global/common/software/nersc"}
    if system == "perlmutter":
        if variant == "cpu:gnu":
            config["MPICC"] = "cc -shared"
        elif variant == "gpu:gnu":
            config["MPICC"] = "cc -target-accel=nvidia80 -shared"
        elif variant == "gpu:nvidia":
            config["MPICC"] = "cc -target-accel=nvidia80 -shared" 
            config["CC"] = "nvc"
            config["CFLAGS"] = "-noswitcherror"
        else:
            raise RuntimeError(f"Unknown {variant=} on {system=}")
    elif system == "cori":
        if variant == "gnu":
            config["MPICC"] = "cc -shared"
        else:
            raise RuntimeError(f"Unknown {variant=} on {system=}")
    else:
        raise RuntimeError(f"Unknown {system=}")

    return config


def init(system: str, variant: str) -> str:
    logger.debug(f"{system=}, {variant=}")

    if system == "perlmutter":
        if variant == "cpu:gnu":
            return "module load PrgEnv-gnu"
        elif variant == "gpu:gnu":
            return "module load PrgEnv-gnu cudatoolkit"
        elif variant == "gpu:nvidia":
            return "module load PrgEnv-nvidia cudatoolkit"
        else:
            raise RuntimeError(f"Unknown {variant=} on {system=}")
    elif system == "cori":
        if variant == "gnu":
            return "module swap PrgEnv-${PE_ENV,,} PrgEng-gnu" 
        else:
            raise RuntimeError(f"Unknown {variant=} on {system=}")
    else:
        raise RuntimeError(f"Unknown {system=}")


def sanity(system: str, variant: str, config: dict[str, str]) -> bool:
    logger.debug(f"{system=}, {variant=}, {config=}")

    import mpi4py
    mpi4py_config = mpi4py.get_config()
    logger.debug(f"Sanity: {mpi4py_config=}")
    return mpi4py_config['mpicc'].endswith(config["MPICC"])