#!/usr/bin/env bash
# Hello, NativeHTMLKit CLI: ask the user to pick fruit in a native window.
#
# Teaches: piping lines into `nativehtmlkit select --multi` and reacting to its exit status.
# Run:     bash hello-cli.sh [--timeout SECONDS]
# Guide:   docs/getting-started/cli.md
set -euo pipefail
status=0
picked=$(printf '%s\n' apple banana cherry | nativehtmlkit select --multi --title "Pick fruit" "$@") || status=$?
case $status in
  0) echo "You picked:"; printf '%s\n' "$picked" | sed 's/^/  /' ;;
  2) echo "Cancelled" >&2 ;;
  124) echo "No answer in time" >&2 ;;
  *) echo "nativehtmlkit failed (exit $status)" >&2 ;;
esac
exit "$status"
