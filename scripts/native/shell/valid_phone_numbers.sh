#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
awk '/^([0-9][0-9][0-9]-|\([0-9][0-9][0-9]\) )[0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]$/ { print }'
