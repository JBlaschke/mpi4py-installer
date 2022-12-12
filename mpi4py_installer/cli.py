from . import logger, load_site, pip_find_mpi4py, pip_cmd, is_system_prefix
from . import pip_uninstall_mpi4py, pip_install_mpi4py

from .sites import auto_site

import argparse


def run():
    parser = argparse.ArgumentParser(
        prog = "mpi4py-installer",
        description = "Make (re)installing mpi4py on HPC systesm easy."
    )
    parser.add_argument(
        "--site", type=str,
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
    parser.add_argument(
        "--system", type=str,
        help="Overwrite the installer's target system"
    )
    parser.add_argument(
        "--show-variants", action="store_true",
        help="Display variants for this site and system"
    )

    args = parser.parse_args()

    logger.setLevel(args.log_level)
    logger.debug(f"Runtime arguments={args}")

    if args.site is None:
        dsite = auto_site()
        if dsite == None:
            raise RuntimeError("You must specify a site")
        logger.info(f"Determined site as: {dsite}")
        site = load_site(dsite)
    else:
        site = load_site(args.site)

    if args.system is None:
        system = site.determine_system()
        logger.info(f"Determined system as: {system}")
    else:
        system = args.system
        logger.info(f"Using: {system=}")

    if args.variant is None:
        variant = site.auto_variant(system)
        logger.info(f"Automatically setting {variant=}")
    else:
        variant = args.variant

    if args.show_variants:
        print(f"Available variants for {system=}")
        auto_variant = site.auto_variant(system)

        for v in site.available_variants(system):
            if v == auto_variant:
                print(f"  * {v}")
            else:
                print(f"    {v}")

        exit(0)

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

    logger.info("Installing mpi4py")
    pip_install_mpi4py(pip_cmd_str, site.init(system, variant))

    logger.info("Checking mpi4py install config")
    sanity = site.sanity(system, variant, config)
    logger.info(f"{sanity=}")
    if not sanity:
        logger.critical("Sanity check FAILED")

