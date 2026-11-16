# Screenshots and media

The images on this site and in the READMEs are clearly labelled **illustrations**, not captured screenshots. Real captures are added only after an interactive check on the target desktop. Pages mark the places for them with an HTML comment such as `<!-- screenshot: tutorial-python-notes -->`; the comment names the example to capture.

## Capturing a screenshot

1. Install the **exact released** packages on the target desktop (KDE Plasma Wayland or Windows) and note the OS, runtime and package versions.
2. Run the example named in the page's screenshot marker, for example `python examples/tutorials/python-notes/notes.py`, or one of the galleries (`examples/python-sdk/gallery.py`, `examples/python-ui/gallery.py`, `examples/powershell-sdk/gallery.ps1`, `examples/powershell-ui/gallery.ps1`).
3. Exercise the controls the page describes. Note anything that fails before capturing; never present a capture of a broken state as working.
4. Capture only the application window. Remove or blur personal data, host names, user names, tokens and file paths.
5. Store the reviewed image under `docs/assets/` and replace the marker with the image and a caption that states the platform and versions. Record the capture's provenance (tool, OS, versions, date, hash, redactions) in `assets/README.md`.

For short motion clips, record locally and keep them small; documentation must still make sense without motion and with reduced motion enabled.
