# Capture screenshots and short demos

The landing and Python marketplace README files include a clearly labeled **illustration**, not a captured UI screenshot. The placeholder PNG is deliberately visible as a temporary onboarding illustration. The deployment bundle includes `scripts/media/capture-linux.sh` (Wayland/`grim`), `scripts/media/capture-windows.ps1` (interactive Windows session) and `scripts/media/make-gif.sh` (`ffmpeg`, if installed).

## Procedure

1. Build/install **exact published** SDK packages on the target desktop. Record OS version, runtime and Core/SDK package versions.
2. Run `examples/python-sdk/gallery.py`, `examples/powershell-sdk/gallery.ps1`, `examples/python-ui/gallery.py`, `examples/powershell-ui/gallery.ps1` separately.
3. Exercise every visible control. Note any failed/no-op behavior before taking captures. Never claim a demo works just because its source compiles.
4. Capture the application window. Crop/blur personal data, internal hostnames, tokens, file paths and account names.
5. Stage a reviewed capture, preserving its identity and original version details:

   ```bash
   python3 scripts/media/stage_screenshot.py --source /path/to/capture.png --platform linux --kind python-sdk
   python3 scripts/media/stage_screenshot.py --source /path/to/capture.png --platform linux --kind python-sdk --apply --promote --reviewed
   ```

   `--promote` updates the public README and (for Python demos) the corresponding marketplace README image. Read the resulting diff before committing. Use `--kind powershell-ui` or other gallery names as appropriate. Store full capture provenance in `assets/README.md`.
6. For motion examples, record a short screen capture locally and convert with the included GIF script. Avoid huge looping GIFs in the README; prefer linked short demos.

The GIF workflow is optional; documentation must still make sense in text and with reduced motion enabled.
