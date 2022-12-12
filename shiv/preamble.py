#!/usr/bin/env python
# -*- coding: utf-8 -*-
import shutil

from pathlib import Path

# These variables are injected by shiv.bootstrap
site_packages: Path
env: "shiv.bootstrap.environment.Environment"

# Get a handle of the current PYZ's site_packages directory
current = site_packages.parent

# The parent directory of the site_packages directory is our shiv cache
cache_path = current.parent

name_p = current.name.split('_')
build_id = name_p[-1]
# The `mpi4py_installer` name contains an underscore, so we have to put the
# first occurance of `_` back into the name after `split` has removed it.
name = "_".join(name_p[:-1])

if __name__ == "__main__":
    for path in cache_path.iterdir():
        if path.name.startswith(f"{name}_") and not path.name.endswith(build_id):
            shutil.rmtree(path)
