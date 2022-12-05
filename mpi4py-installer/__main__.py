from . import logger, load_site, pip_find_mpi4py, pip_cmd, is_system_prefix
from . import pip_uninstall_mpi4py, pip_install_mpi4py

import argparse


def run():
    parser = argparse.ArgumentParser(
        prog = "mpi4py-installer",
        description = "Make (re)installing mpi4py on HPC systesm easy."
    )
    parser.add_argument(
        "--site", type=str, default="nersc",
        help="Install site. (default=nersc)"
    )
    parser.add_argument(
        "--log-level", type=int, default=20,
        help="Python logger logging level. (default=20)"
    )
    parser.add_argument(
        "--variant", type=str,
        help="Install variant"
    )

    args = parser.parse_args()

    logger.setLevel(args.log_level)
    logger.debug(f"Runtime arguments={args}")

    site = load_site(args.site)
    system = site.determine_system()
    logger.info(f"Determined system as: {system}")

    if args.variant is None:
        variant = site.auto_variant(system)
        logger.info(f"Automatically setting {variant=}")
    else:
        variant = args.variant

    config = site.config(system, variant)
    logger.debug(f"Loaded {config=}")

    has_mpi4py = pip_find_mpi4py()
    logger.info(f"{has_mpi4py=}")

    if has_mpi4py:
        logger.info("mpi4py install detected! uninstalling current version")
        pip_uninstall_mpi4py()

    if is_system_prefix(config):
        logger.warning(" ".join([
            "Your python version shares the system prefix.",
            "Did you forget to activate your python environment?"
        ]))

    pip_cmd_str = pip_cmd(config)
    logger.info(f"{pip_cmd_str=}")

    logger.info(f"Installing mpi4py using {pip_cmd_str=}")
    pip_install_mpi4py(pip_cmd_str, site.init(system, variant))


if __name__ == "__main__":
    run()