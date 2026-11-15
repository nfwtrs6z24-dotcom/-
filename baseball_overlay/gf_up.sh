#!/bin/bash
# usage: gf_up.sh <file> <server> <lifetime>
set -u
F="$1"; SERVER="$2"; LIFE="$3"
W="${OVERLAY_WORK:-$(cd "$(dirname "$0")" && pwd)}"
CH=$W/chunk.bin
CS=$((100*1024*1024))
SIZE=$(stat -c %s "$F")
N=$(( (SIZE + CS - 1) / CS ))
ID=$(od -An -N16 -tx4 /dev/urandom | tr -d ' \n')
NAME=$(basename "$F")
echo "id=$ID chunks=$N"
for ((i=0;i<N;i++)); do
  dd if="$F" of=$CH bs=$CS skip=$i count=1 status=none
  for try in 1 2 3 4 5 6; do
    R=$(curl -sS -b $W/gf_cj -c $W/gf_cj --max-time 900 \
      -F "id=$ID" -F "name=$NAME" -F "chunk=$i" -F "chunks=$N" -F "lifetime=$LIFE" \
      -F "file=@$CH;filename=blob;type=application/octet-stream" \
      "https://$SERVER/upload_chunk.php")
    if echo "$R" | grep -q '"status":0'; then break; fi
    echo "chunk $i try $try failed: $R"; sleep $((2**try))
  done
  echo "chunk $((i+1))/$N: $R"
done
rm -f $CH
