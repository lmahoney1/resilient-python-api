#!/bin/bash -e
RCFILE="./travis-scripts/travis-configs/banditconfig.yaml"
# Run a Bandit scan on all packages
# Bandit configurgation is pulled from a yaml file

# TODO: Bandit gives us information on vulnerbilities that could exist today
# if we depend on its exit code the builds will fail until we fix or ignore the specific instances
# for this reason, --exit-zero to give the team information on things to change.
# --exit-zero should be removed at a later point.
bandit -r . --configfile $RCFILE || exit 0

