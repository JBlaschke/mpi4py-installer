import json
import os
import subprocess
import sys

from contextlib import AbstractContextManager


class BashRunner(AbstractContextManager):
    """Run multiple bash scripts with persisent environment.

    Environment is stored to "env" member between runs. This can be updated
    directly to adjust the environment, or read to get variables.
    """

    def __init__(self, env=None):
        if env is None:
            env = dict(os.environ)
        self.env: Dict[str, str] = env

        self._fd_read, self._fd_write = os.pipe()
        write_env_pycode = ";".join([
            "import os",
            "import json",
            "env_json = json.dumps(dict(os.environ)).encode()",
            f"os.write({self._fd_write}, env_json)",
            f"os.write({self._fd_write}, \"\\0\".encode())"
        ])
        self._env_snapshot = "\n".join([
            "__bashrunner_exit_code_trap=$?",
            f"{sys.executable} -c '{write_env_pycode}'",
            "exit $__bashrunner_exit_code_trap"
        ])


    def run(self, cmd, **opts):
        if self._fd_read is None:
            raise RuntimeError("BashRunner is already closed")

        cmd += "\n" + self._env_snapshot
        result = subprocess.run(
            ["bash", "-c", cmd],
            pass_fds=[self._fd_write],
            env=self.env,
            **opts
        )

        # HAXOR: bit of a hack, but we don't know how long the env json will be.
        # TODO: performance optimization: pass the length as the first byte.
        env_json = ""
        for block in iter(lambda: os.read(self._fd_read, 1), "\0".encode()):
            env_json_chunk = block.decode()
            env_json = env_json + env_json_chunk
        self.env = json.loads(env_json)

        return result


    def __exit__(self, exc_type, exc_value, traceback):
        if self._fd_read:
            os.close(self._fd_read)
            os.close(self._fd_write)
            self._fd_read = None
            self._fd_write = None


    def __del__(self):
        self.__exit__(None, None, None)
