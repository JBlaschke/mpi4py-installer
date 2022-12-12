#!/usr/bin/env bash

ver="0.3.0"
src="JBlaschke/mpi4py-installer"
name="mpi4py_installer"

# Arrange for the temporary file to be deleted when the script terminates
trap 'rm -f "/tmp/exec.$$"' 0
trap 'exit $?' 1 2 3 15

# Create temporary file from curl
curl -fsSL https://github.com/${src}/raw/main/shiv/dist/${name}-${ver}.pyz >/tmp/exec.$$

# Make the temporary file executable
chmod +x /tmp/exec.$$

# Execute the temporary file
/tmp/exec.$$ $@
