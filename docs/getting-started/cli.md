# CLI in five minutes

The `nativehtmlkit` command (alias `nhk`) shows a native window from any shell: pick rows (`select`), read text (`view`) or fill an HTML form (`form`). Input comes from stdin or a file, the result goes to stdout, and the exit status says what happened.

## 1. Install

Download the archive for your platform from the [CLI releases](https://github.com/nativehtmlkit/nativehtmlkit-cli/releases) (`nativehtmlkit-cli-v0.1.2-linux-x64.tar.gz` or `nativehtmlkit-cli-v0.1.2-windows-x64.zip`) and verify it against the release's `SHA256SUMS` before you run anything:

```bash
sha256sum -c SHA256SUMS --ignore-missing
tar xzf nativehtmlkit-cli-v0.1.2-linux-x64.tar.gz
export PATH="$PWD/nativehtmlkit-cli-v0.1.2-linux-x64:$PATH"
nativehtmlkit --version && nativehtmlkit doctor
```

The archive contains `nativehtmlkit`, the `nhk` alias, the bundled `nativehtmlkit-host` (Core 1.0.3), licences and an example form. Keep the files together: the CLI finds the host next to itself (or use `--host PATH`).

## 2. Write `hello-cli.sh`

<!-- include: examples/getting-started/hello-cli.sh -->
```bash title="examples/getting-started/hello-cli.sh"
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
```
<!-- /include -->

## 3. Run it

```bash
bash hello-cli.sh
bash hello-cli.sh --timeout 10    # give up after ten seconds (exit status 124)
```

<!-- screenshot: getting-started-hello-cli -->

## Exit statuses

| Status | Meaning |
|---|---|
| 0 | The user submitted (or closed a `view`); the selection is on stdout |
| 1 | Error (bad input, host problem); details on stderr |
| 2 | The user cancelled or closed the window |
| 124 | `--timeout` expired before the user decided |
| 130 / 143 / 129 | Interrupted by SIGINT / SIGTERM / SIGHUP |

`select` writes the selection only on success, so a script can always trust stdout when the status is 0.

## More commands

```bash
printf 'name,status\nweb,up\ndb,down\n' | nativehtmlkit select --input-format csv --multi --output-format json
printf 'line one\nline two\n' | nativehtmlkit view --title "Release notes"
nativehtmlkit form --html examples/sample-form.html     # trusted HTML containing <form id="nhk-form">
```

## Next steps

- Tutorial: [a Git branch picker](../tutorials/cli-branch-picker.md).
- Exact flags, formats and limits: [CLI reference](https://github.com/nativehtmlkit/nativehtmlkit-cli/blob/main/docs/REFERENCE.md), or `nativehtmlkit <command> --help`.
