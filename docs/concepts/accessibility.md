# Accessibility basics

NativeHTMLKit builds a native accessibility tree from your HTML (AccessKit, exposed through AT-SPI on Linux and UI Automation on Windows). Screen readers see roles, names and states derived from your markup, so ordinary semantic HTML is the most important tool.

## Checklist

- **Use real elements.** `<button>` for actions, `<a href>` for links, `<input>`/`<select>`/`<textarea>` for input, headings in order, lists for lists, `<table>` with `<th>` for tables. A `<div>` with a click handler is neither focusable nor announced as a button.
- **Name every control.** Use `<label for="id">` (or wrap the control in `<label>`); add `aria-label` only where no visible label exists, such as a search field.
- **Announce status changes.** Put status text in an element with `role="status"` (polite) or `role="alert"` (important), and update it with `set_text`. The UI libraries' `alert` component uses `role="status"`.
- **Keep keyboard paths.** Everything must work with Tab, Shift+Tab, Enter and Space. Forms submit with Enter; modal `<dialog>`s close with Escape. Move focus deliberately after actions (`document.focus(id)`, `Set-NativeHTMLKitFocus`), as the todo tutorial does after adding an item.
- **Do not rely on colour alone.** Pair colour with text or icons (for example, show a service state as text inside a coloured pill).
- **Respect preferences.** Style for `prefers-color-scheme` and `prefers-reduced-motion`; [Style with the supported CSS](../sdk/python/guides/styling-and-layout.md) shows how.
- **Give images text.** Every `<img>`, including live bitmaps, needs a meaningful `alt`; keep values you draw in a chart available as HTML text too ([Live bitmap charts](../sdk/python/guides/live-bitmaps.md)).

## Check what assistive technology sees

The `get_accessibility_tree` document operation returns the tree the host exposes (roles, names, states, relations, bounds). Read it to confirm, for example, that the fields of a [sign-up form](../sdk/python/guides/forms-and-validation.md) are named "E-mail" and "Repeat password":

```python
tree = doc.command("get_accessibility_tree")["tree"]
names = [(node["role"], node["name"]) for node in tree["nodes"] if node["name"]]
```

PowerShell: `Invoke-NativeHTMLKitDocumentCommand -Document $doc -Operation get_accessibility_tree`.

This is a quick structural check, not a substitute for testing with a screen reader (Orca on Linux, Narrator or NVDA on Windows).

## Known limitations

Screen-reader coverage is still being qualified. Core 1.0.3 has a reported Orca issue with collapsed `<select>` announcements on Linux, and UI-library-specific screen-reader coverage is incomplete; see [limitations](../capabilities/limitations.md).
