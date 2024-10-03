from . import logger, load_site, load_user_site, pip_find_mpi4py, pip_cmd, \
    is_system_prefix, pip_uninstall_mpi4py, pip_install_mpi4py

from .sites import auto_site, Site

import argparse


def run():
    """
    Run the mpi4py installer CLI using ArgumentParser inputs
    """
    # Set up CLI 
    parser = argparse.ArgumentParser(
        prog="mpi4py-installer",
        description="Make (re)installing mpi4py on HPC systesm easy."
    )
    parser.add_argument(
        "--site", type=str,
        help="Install site (uses `auto_site` by default)"
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
    parser.add_argument(
        "--user", action="store_true",
        help="Install to USER_BASE instead"
    )
    parser.add_argument(
        "--overwrite_system", action="store_true",
        help="Overwrite system prefix"
    )

    args = parser.parse_args()

    # Set Logger Level
    logger.setLevel(args.log_level)
    logger.debug(f"Runtime arguments={args}")

    # Populate settings on any configured sites -- this is a signleton class,
    # once constructed, the constructor does not search for site modules
    # again -- instead using the cached information.
    site_info = Site()

    # Load site -- if no site is provided, use the auto_site function, which
    # will run check_site for each of the available sites.
    if args.site is None:
        dsite, flag = auto_site()
        if dsite == None:
            logger.critical(
                "Could not decide on which site to use automatically."
            )
            print("Valid sites are:")
            print(f"In mpi4py_installer.sites: {site_info.sites}")
            print(f"In {site_info.user_path}: {site_info.user_sites}")
            raise RuntimeError("You must specify a site")

        logger.info(f"Determined site as: {dsite}")

        assert dsite is not None  # coerce mypy type narrowing
        if flag:
            site = load_user_site(dsite, site_info.user_path)
        else:
            site = load_site(dsite)
    else:
        if args.site in site_info.sites:
            site = load_site(args.site)
        elif args.site in site_info.user_sites:
            site = load_user_site(args.site, site_info.user_path)
        else:
            mod_sites = site_info.sites
            usr_sites = site_info.user_sites
            logger.critical(
                f"Site {args.site} not in {mod_sites=} nor {usr_sites=}"
            )
            raise RuntimeError(f"{args.site} could not be found")

    # Set the system using `determine_system` -- the CLI flag can be used to
    # overwrite the output from `determine_system`.
    if args.system is None:
        system = site.determine_system()
        logger.info(f"Determined system as: {system}")
    else:
        system = args.system
        logger.info(f"Using: {system=}")

    # If the CLI specifies `show_variants`, then print all avalailable variants,
    # and exit (do not install anything). The result returned by `auto_variant`
    # is highlighted using `*`
    if args.show_variants:
        print(f"Available variants for {system=}")
        auto_variant = site.auto_variant(system)

        for v in site.available_variants(system):
            if v == auto_variant:
                print(f"  * {v}")
            else:
                print(f"    {v}")

        exit(0)

    # Set the variant: if no variant is specified on the CLI, then the site's
    # `auto_variant` is used.
    if args.variant is None:
        variant = site.auto_variant(system)
        logger.info(f"Automatically setting {variant=}")
    else:
        variant = args.variant

    config = site.config(system, variant)
    logger.debug(f"Loaded {config=}")

    has_mpi4py = pip_find_mpi4py()
    logger.info(f"{has_mpi4py=}")

    if is_system_prefix(config):
        logger.warning(" ".join([
            "Your python version shares the system prefix.",
            "Did you forget to activate your python environment?"
        ]))

        if not args.overwrite_system:
            logger.critical(" ".join([
                "Will not overwrite install in system prefix. Use: "
                "--overwrite_system to force install in system prefix."
            ]))

            exit(1)

    if has_mpi4py:
        logger.info("mpi4py install detected! uninstalling current version")
        pip_uninstall_mpi4py()

    pip_cmd_str = pip_cmd(config)

    logger.info("Installing mpi4py")
    pip_install_mpi4py(pip_cmd_str, args.user, site.init(system, variant))

    logger.info("Checking mpi4py install config")
    sanity = site.sanity(system, variant, config)
    logger.info(f"{sanity=}")
    if not sanity:
        logger.critical("Sanity check FAILED")

