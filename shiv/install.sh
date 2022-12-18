#!/usr/bin/env bash

src="JBlaschke/mpi4py-installer"
name="mpi4py_installer"
tmpdir=$(mktemp -d)

# Arrange for the temporary file to be deleted when the script terminates
trap 'rm -r "${tmpdir}"' 0
trap 'exit $?' 1 2 3 15

# Create temporary file from curl
curl -fsSL                                                         \
    https://github.com/${src}/releases/latest/download/${name}.pyz \
    > ${tmpdir}/exec.$$

# Make the temporary file executable
chmod +x ${tmpdir}/exec.$$

# Execute the temporary file
${tmpdir}/exec.$$ $@
