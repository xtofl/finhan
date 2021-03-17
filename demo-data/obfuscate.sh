#!/bin/bash
# Obfuscate 'raw' bepost csv's and render a plot
#

function find_accounts() {
	grep --no-filename --extended-regexp --only-matching 'BE[0-9]{10}' raw/* | sort | uniq
}

find_accounts > _accounts
seq 1 $(wc -w < _accounts) | xargs printf 'BE%08d\n' > _replacements

paste _accounts _replacements | while read acc rep; do
	echo "s/$acc/$rep/g;"
done > replace.sed

mkdir -p obfuscated
for f in raw/*.csv; do
	sed --file=replace.sed < $f > "obfuscated/$(basename $f)"
done

sed --file=replace.sed < balance.yaml > obfuscated/balance.yml

finhan-view --balance obfuscated/balance.yml obfuscated/*.csv
