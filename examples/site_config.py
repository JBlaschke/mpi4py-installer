from mpi4py_installer import logger


def config(variant):
    logger.info(f"Entered local site config / config: {variant=}")
    config = dict()
    config["sys_prefix"] = "None"
    config["MPICC"] = "mpicc"
    return config


def init(variant):
    logger.info(f"Entered local site config / init: {variant=}")
    return ""