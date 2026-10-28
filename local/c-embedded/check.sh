#!/usr/bin/env bash
# check.sh: compile, run, and diff a C exercise. Run it INSIDE the Ubuntu VM.
#
# Usage:
#   bash check.sh path/to/file.c                 # finds file.expected.txt itself
#   bash check.sh path/to/file.c path/to/expected.txt
#
# What it does (the same three stages as a PLC download-and-verify):
#   1. compile with gcc -Wall -Wextra -Werror -std=c11  (any warning = fail)
#   2. run the program (10 second limit, in case loop() never ends)
#   3. compare its stdout with the expected-output file, line by line
#
# Where it looks for the expected output, when you do not pass one:
#   - next to your .c file:            <name>.expected.txt
#   - in the course copy of the track: local/c-embedded/*/<name>.expected.txt
#
# If bash says "bad interpreter" or "$'\r': command not found", the file got
# Windows line endings. Fix it once with:   sed -i 's/\r$//' check.sh

set -u

usage() {
    echo "Usage: bash check.sh path/to/file.c [path/to/expected.txt]"
}

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    usage
    exit 2
fi

src="$1"
if [ ! -f "$src" ]; then
    echo "No such file: $src"
    exit 2
fi
case "$src" in
    *.c) ;;
    *) echo "check.sh expects a .c file (got: $src)"; usage; exit 2 ;;
esac

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
name="$(basename "$src" .c)"

expected=""
if [ $# -eq 2 ]; then
    expected="$2"
    if [ ! -f "$expected" ]; then
        echo "No such expected-output file: $expected"
        exit 2
    fi
else
    for cand in "${src%.c}.expected.txt" "$script_dir"/*/"$name.expected.txt"; do
        if [ -f "$cand" ]; then
            expected="$cand"
            break
        fi
    done
fi

if ! command -v gcc > /dev/null 2>&1; then
    echo "gcc was not found. Install the toolchain first:"
    echo "  sudo apt update && sudo apt install build-essential"
    exit 2
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

echo "== 1/3 compile: gcc -Wall -Wextra -Werror -std=c11 $src"
if ! gcc -Wall -Wextra -Werror -std=c11 "$src" -o "$tmp/$name"; then
    echo
    echo "FAIL (compile). Warnings count as errors here."
    echo "Read the FIRST message above (file:line:column), fix that one, and re-run."
    exit 1
fi
echo "   compiled OK"

echo "== 2/3 run: ./$name"
timeout 10 "$tmp/$name" > "$tmp/out.raw"
status=$?
tr -d '\r' < "$tmp/out.raw" > "$tmp/out.txt"
cat "$tmp/out.txt"
if [ $status -eq 124 ]; then
    echo "FAIL (run): still running after 10 s. Is there a loop that never ends?"
    exit 1
fi
if [ $status -ne 0 ]; then
    echo "FAIL (run): the program exited with status $status. main() should return 0."
    exit 1
fi

echo "== 3/3 compare"
if [ -z "$expected" ]; then
    echo "No $name.expected.txt found, so there is nothing to compare."
    echo "Compile and run passed."
    exit 0
fi
tr -d '\r' < "$expected" > "$tmp/expected.txt"
if diff -u --label expected --label yours "$tmp/expected.txt" "$tmp/out.txt" > "$tmp/diff.txt"; then
    echo "PASS: output matches $expected"
    exit 0
fi
echo "FAIL (output). Lines starting with '-' are expected; '+' lines are what yours printed:"
cat "$tmp/diff.txt"
echo "Look for spelling, spaces, and a missing \\n at the end of a line."
exit 1
