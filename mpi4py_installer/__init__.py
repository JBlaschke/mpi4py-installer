from .runners   import ShellRunner
from .singleton import Singleton

import sys
import logging
import importlib

from pathlib             import Path
from importlib.machinery import SourceFileLoader
from types               import ModuleType


logger = logging.getLogger(__name__)
FORMAT = "[%(levelname)8s | %(filename)s:%(lineno)s - %(module)s.%(funcName)s() ] %(message)s"
logging.basicConfig(format=FORMAT)


def load_site(site: str) -> ModuleType:
    """
    load_site(site: str) -> ModuleType


    Loads a site module stored in the `mpi4py_installer.sites` tree. The loaded
    module is returned as a python module (to be used later on).
    """

    logger.debug(f"Loading site: {site}")
    site_module = importlib.import_module(
        f".sites.{site}", package="mpi4py_installer"
    )
    return site_module


def load_user_site(user_site:str , user_site_root: Path) -> ModuleType:
    """
    load_user_site(user_site:str , user_site_root: Path) -> ModuleType


    Loads a user-defined site module stored at `user_site_root`. The loaded
    moduel is returned as a python module (to be used later on).
    """
    logger.debug(f"Loading user site: {user_site} at {user_site_root}")
    return SourceFileLoader(
        "user_site", str(user_site_root / Path(user_site + ".py"))
    ).load_module()


def pip_find_mpi4py():
    logger.debug("Checking for installed versions of mpi4py")
    
    with ShellRunner() as bash_runner:
        out = bash_runner.run(
            f"{sys.executable} -m pip freeze",
            capture_output=True
        )

        logger.debug(f"stderr={out.stderr.decode()}")
        out.check_returncode()
        logger.debug(f"stderr={out.stdout.decode()}")

        for p in out.stdout.decode().split("\n"):
            package = p.split("==")
            if package[0] == "mpi4py":
                logger.debug(f"Found mpi4py: {package}")
                return True

    logger.debug("Did not find mpi4py")
    return False


def is_system_prefix(config):
    return sys.prefix.startswith(config["sys_prefix"])


def pip_cmd(config):
    logger.debug("Configuring pip command")

    pip_cmd = ""

    if "MPICC" in config:
        pip_cmd += f"MPICC=\"{config['MPICC']}\""
        pip_cmd += " "
    if "CC" in config:
        pip_cmd += f"CC=\"{config['CC']}\""
        pip_cmd += " "
    if "CFLAGS" in config:
        pip_cmd += f"CFLAGS=\"{config['CFLAGS']}\""
        pip_cmd += " "
    if "LDFLAGS" in config:
        pip_cmd += f"LDFLAGS=\"{config['LDFLAGS']}\""
        pip_cmd += " "

    pip_cmd += f"{sys.executable} -m pip"
    pip_cmd += " "

    logger.debug(f"Done configuring pip command")

    return pip_cmd.strip()  # clean up any unnecessary spaces 


def pip_uninstall_mpi4py():
    logger.debug(f"Uninstalling mpi4py")

    with ShellRunner() as bash_runner:
        out = bash_runner.run(
            f"{sys.executable} -m pip uninstall -y mpi4py",
            capture_output=True
        )

        logger.debug(f"stderr={out.stderr.decode()}")
        out.check_returncode()
        logger.debug(f"stdout={out.stdout.decode()}")

    logger.debug("Done uninstalling mpi4py")


def pip_install_mpi4py(pip_cmd, use_user, init):
    logger.debug(f"Installing mpi4py")

    cmd = f"{pip_cmd} " + "install --no-cache-dir --no-binary=:all: mpi4py"
    if use_user:
        cmd += " --user"

    with ShellRunner() as bash_runner:
        logger.info(f"Running init command: {init}")  # TODO: skip if None
        out = bash_runner.run(init, capture_output=True)

        logger.debug(f"stderr={out.stderr.decode()}")
        out.check_returncode()
        logger.debug(f"stdout={out.stdout.decode()}")

        logger.info(f"Running install command: {cmd}")
        out = bash_runner.run(cmd, capture_output=True)

        logger.debug(f"stderr={out.stderr.decode()}")
        out.check_returncode()
        logger.debug(f"stdout={out.stdout.decode()}")

    logger.debug("Done installing mpi4py")
