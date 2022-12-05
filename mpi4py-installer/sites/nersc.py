from os import environ


def determine_system():
    return environ["NERSC_HOST"]


def auto_variant(system):
    if system == "perlmutter":
        return "gpu:gnu"
    else:
        raise RuntimeError(f"Unknown {system=}")


def config(system, variant):
    config = {"sys_prefix": "/global/common/software/nersc"}

    if system == "perlmutter":
        if variant == "cpu:gnu":
            config["MPICC"] = "cc -shared"
        elif variant == "gpu:gnu":
            config["MPICC"] ="cc -target-accel=nvidia80 -shared"
        elif variant == "gpu:nvidia":
            config["MPICC"] = "cc -target-accel=nvidia80 -shared" 
            config["CC"] = "nvc"
            config["CFLAGS"] = "-noswitcherror"
        else:
            raise RuntimeError(f"Unknown {variant=} on {system=}")
    else:
        raise RuntimeError(f"Unknown {system=}")

    return config


def init(system, variant):
    if system == "perlmutter":
        if variant == "cpu:gnu":
            return "module load PrgEnv-gnu"
        elif variant == "gpu:gnu":
            return "module load PrgEnv-gnu cudatoolkit"
        elif variant == "gpu:nvidia":
            return "module load PrgEnv-nvidia cudatoolkit"
        else:
            raise RuntimeError(f"Unknown {variant=} on {system=}")
    else:
        raise RuntimeError(f"Unknown {system=}")
