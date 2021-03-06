#!/bin/bash
# Obfuscate 'raw' bepost csv's and render a plot
#
set -euo pipefail

case ${1-} in
  -h|--help) cat <<END_OF_HELP
Use this script to obfuscate a set of raw bepost csv files: it scans
all account IDs and replaces them with sequential numbers.

Usage:
  [env-vars] $0 [-h|--help]

Environment:
  * RAW_DATA_DIR: directory with bepost .csv files
  * NAMES_FILE: sed commands to replace people's names
  * VIEW: optional, if not empty, will also call finhan-view to visualize
    the data.

END_OF_HELP
  exit 0
  ;;
esac

echo RAW_DATA_DIR=${RAW_DATA_DIR}

BALANCE_FILE=${BALANCE_FILE:-balance.yaml}
echo BALANCE_FILE=${BALANCE_FILE}

if [ ! -f "$NAMES_FILE" ]; then
  echo "I need a file to obfuscate person names in NAMES_FILE"
  exit 1
fi


function find_accounts() {
	grep --no-filename --extended-regexp --only-matching 'BE[0-9]+' $RAW_DATA_DIR/*.csv | sort | uniq
}

find_accounts > _accounts
seq 1 $(wc -w < _accounts) | xargs printf 'BE%08d\n' > _replacements

paste _accounts _replacements | while read acc rep; do
	echo "s/$acc/$rep/g"
done > replace.sed

cat $NAMES_FILE >> replace.sed

mkdir -p obfuscated
for f in $RAW_DATA_DIR/*.csv; do
	sed -E --file=replace.sed < $f > "obfuscated/$(basename $f | sed -E --file=replace.sed)"
done

sed --file=replace.sed < $BALANCE_FILE > obfuscated/$BALANCE_FILE

[ -z "${VIEW:-}" ] || finhan-view --balance obfuscated/$BALANCE_FILE obfuscated/*.csv
