from .runners import ShellRunner 

import sys
import logging
import importlib


logger = logging.getLogger(__name__)
FORMAT = "[%(levelname)8s | %(filename)s:%(lineno)s - %(module)s.%(funcName)s() ] %(message)s"
logging.basicConfig(format=FORMAT)


def load_site(site):
    logger.debug(f"Loading site: {site}")
    site_module = importlib.import_module(
        f".sites.{site}", package="mpi4py_installer"
    )
    logger.debug("Done loading site")
    return site_module


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
    use_user = is_system_prefix(config)

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

    pip_cmd += f"{sys.executable} -m pip"
    pip_cmd += " "

    if use_user:
        pip_cmd += "--user"

    logger.debug(f"Done configuring pip command")

    return pip_cmd


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


def pip_install_mpi4py(pip_cmd, init):
    cmd = f"{pip_cmd} "+ "install --no-cache-dir --no-binary=:all: mpi4py"
    logger.debug(f"Installing mpi4py")

    with ShellRunner() as bash_runner:
        logger.info(f"Running init command: {init}")
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