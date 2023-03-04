from .. import load_site, logger


# register new sites here
available_sites = [
    "local",
    "nersc"
]


def auto_site() -> str:
    """
    auto_site() -> str


    Check each of the sites registered in `available_sites` if it's `check_site`
    returns true.

    * If one site's `check_site` returns `True` return that site's name.
    * If more than one site's `check_site` returns `true` then return `None`
    """
    logger.debug("Searching for compatible sites")

    found = None
    for s in available_sites:
        site = load_site(s)
        if (found is None) and site.check_site():
            logger.debug(f"Found: site={s}")
            found = s
        elif (found is not None) and site.check_site():
            logger.debug(f"Found second site candidate: {s}")
            logger.critical("Warning multiple compatible sites detected!")
            return None

    return found
