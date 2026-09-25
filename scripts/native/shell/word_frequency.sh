#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
awk '{ for (i=1;i<=NF;i++) count[$i]++ } END { for (word in count) print word, count[word] }' | sort -k2,2nr -k1,1
