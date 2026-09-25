#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
awk 'NR==1 { width=NF }
     NF!=width { bad=1; exit 2 }
     { for (i=1;i<=NF;i++) cell[NR,i]=$i }
     END { if (bad) exit 2;
           for (i=1;i<=width;i++) {
             for (j=1;j<=NR;j++) printf "%s%s", cell[j,i], (j==NR ? "\n" : " ")
           }
     }'
