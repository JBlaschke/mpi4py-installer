#!/usr/bin/env bash

ver=0.3.0

pushd $(readlink -f $(dirname ${BASH_SOURCE[0]}))

shiv .                                       \
    -o shiv/dist/mpi4py_installer-${ver}.pyz \
    -e mpi4py_installer.cli:run              \
    --preamble shiv/preamble.py              \
    --compressed

popd
