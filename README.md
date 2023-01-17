# mpi4py-installer

A simple installer to manage `mpi4py` install variants on HPC systems (using
pip). `mpi4py_installer` uses `pip install --no-cache-dir --no-binary=:all:` to
install `mpi4py`, together with pre-defined compiler definitions. This ensures
that `mpi4py` is built and linked against the system's MPI implementation.

## Features

`mpi4py_installer` is detects the system it's running on automatically -- based
on the site's automatic detection rules. If your site supports full automatic
configuration, then all you need to do is run:

```
curl -fsSL https://github.com/JBlaschke/mpi4py-installer/releases/latest/download/install.sh | sh
```

from within your python or conda environment. For more control, it is
recommended that you `pip install mpi4py-installer` and run `mpi4py_installer`
as a python package.

### Automatic Everything

`mpi4py_installer` detects the site (HPC center) and system that it's running
on. It also comes configured with default build variants for each system. If
you are happy with the sysadmin's defaults, all you need to do is run:

```
python -m mpi4py_installer
```

That's it! But there are many ways you can take control -- as described in the
following sections.

### Automatically Detect System

`mpi4py_installer` uses `<site name>.dertermine_system()` to detect which
system it is running on. For cross-site builds, you can overwrite this using:
`--system=<system name>`. Eg:

```
python -m mpi4py_installer --site=nersc --system=perlmutter
```

### Display Available Variants for a given Site and System:

`mpi4py_installer` uses `<site name>.available_variants(system)` to display the
available build vaiants. Setting `--show-variants` from the CLI activates this
mode. This modes does not install `mpi4py`, instead prints a list of the
avariants (default variant is designated using `*`). E.g:

```
python -m mpi4py_installer --site=nersc --show-variants
```

will display the variants available on this system at NERSC.

### Set Build Variants

The `--variant=<variant name>` input flag sets the build variants. Build
variants can be any string, but the recommended format is:
`system_partition:compiler_name` -- e.g. `gpu:nvidia`. Eg:

```
python -m mpi4py_installer --site=nersc --variant=gpu:nvidia
```

### Logging

By default minimal logging is displayed (after all, this is not drain surgery).
WHen someing goes wrong though, you can enable debug mode by lowering the log
level using the `--log-level=10` flag. The logger is programatically accessible
as: `mpi4py_installer.logger`.

## For Sysadmins

Do you want to add your site or system to the machines supports out-of-the-box?
Easy, submit a PR to add `site_name.py` to `sites/`. `site_name.py` needs to
define the following functions:

* `check_site() -> bool`: a function that is true only when run on your center's
systems -- `mpi4py_installer` will call this function for every registered site.
If more than on site's `check_site()` returns `True`, automatic site resolution
fails. Often this is done by checking for the presence of a particular
environment variable, or the machine's hostname.
* `determine_system() -> str`: a function that can dermine the name
(returned as a string) of the system that it's currently running on. Often this
is done by checking for the presence of a particular environment variable, or
the machine's hostname.
* `available_variants(system: str) -> list[str]` returns a list of all avialable
variants on `system`.
* `auto_variant(system: str) -> str`: a function that returns the name of the
default variant on `system`.
* `config(system: str, variant: str) -> dict[str, str]` returns a dictionary
containing the following keys:
    - `'sys_prefix'`: the path prefix of a system (module) version of python.
    Any python executable that starts with this path will be assumed to have a
    read-only `site-pacakges`.
    - `'CC'`, `'MPICC'`, `'CFLAGS'` control the compiler and `CLFAGS` used by
    the compiler.
* `init(system: str, variant: str) -> str` returns the bash commands that must
preceede the `MPICC=... pip install ...` command. Eg. `module load` statements
go here.
* `sanity(system: str, variant: str, config: dict[str, str]) -> bool` returns
true if the `mpi4py` configuration matches what you expect.

### Local Site Configuration Files

By setting the `MPI4PY_LOCAL` environment variable to point to a local site
configuration file, you can create system-specific local site configs that are
not included in this package (e.g. you might want to set up local configurations
withouth publishing them). Take a look at `examples/site_config.py` for an
example.

### Logging and Debugging

We recommend that you log the inputs to your site-configuration functions, eg:

```python
def sanity(system: str, variant: str, config: dict[str, str]) -> bool:
    logger.debug(f"{system=}, {variant=}, {config=}")
```

This way you can most easily answer trouble-tickets by asking the user to set
`--log-level=10`. Any user configurations that might influence the setup logic
would be apparent here.
