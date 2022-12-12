#!/usr/bin/env bash

ver=0.2.0

pushd $(readlink -f $(dirname ${BASH_SOURCE[0]}))

shiv .                                       \
    -o shiv/dist/mpi4py_installer-${ver}.pyz \
    -e mpi4py_installer.entrypoint           \
    --preamble shiv/preamble.py              \
    --compressed

popd
