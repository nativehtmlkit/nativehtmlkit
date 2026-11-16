# CLI — native select in a pipeline

Download the Linux or Windows x64 executable from the [CLI releases](https://github.com/nativehtmlkit/nativehtmlkit-cli/releases). Verify the published SHA256SUMS before execution. The executable is `nativehtmlkit` (alias `nhk` where installed).

```bash
printf 'alpha
beta
gamma
' | nativehtmlkit select --multi
printf 'name,status
a,up
b,down
' | nativehtmlkit select --input-format csv --multi --output-format json
printf 'one
two
' | nativehtmlkit view
nativehtmlkit doctor
```

`select` writes selected records **only on success** (exit 0), cancel/close uses exit 2, and `--timeout` uses exit 124. `view` is read-only. Input is UTF-8 and bounded. For forms, see `nativehtmlkit form --html examples/sample-form.html` (trusted HTML with `<form id="nhk-form">`). The CLI is independent of the language SDKs.

See [CLI reference](https://github.com/nativehtmlkit/nativehtmlkit-cli/blob/main/docs/REFERENCE.md) for format limits, error codes and lifecycle behavior.
