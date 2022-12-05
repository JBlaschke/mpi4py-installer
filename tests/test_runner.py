from mpi4py_installer.runners import ShellRunner

with ShellRunner() as bash_runner:
    out = bash_runner.run(
        "module swap PrgEnv-${PE_ENV,,} PrgEnv-gnu",
        capture_output=True
    )
    out.check_returncode()
    out = bash_runner.run("echo $PE_ENV", capture_output=True)

    print(f"{out.stderr.decode()=}")
    print(f"{out.stdout.decode()=}")

    out = bash_runner.run(
        "module swap PrgEnv-${PE_ENV,,} PrgEnv-nvidia",
        capture_output=True
    )
    out.check_returncode()
    out = bash_runner.run("echo $PE_ENV", capture_output=True)

    print(f"{out.stderr.decode()=}")
    print(f"{out.stdout.decode()=}")

    out = bash_runner.run(
        "module swap PrgEnv-${PE_ENV,,} PrgEnv-gnu",
        capture_output=True
    )
    out.check_returncode()
    out = bash_runner.run("echo $PE_ENV", capture_output=True)

    print(f"{out.stderr.decode()=}")
    print(f"{out.stdout.decode()=}")

