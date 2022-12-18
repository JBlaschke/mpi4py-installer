#!/usr/bin/env bash

pushd $(readlink -f $(dirname ${BASH_SOURCE[0]}))

shiv .                                \
    -o shiv/dist/mpi4py_installer.pyz \
    -e mpi4py_installer.cli:run       \
    --preamble shiv/preamble.py       \
    --compressed

popd
