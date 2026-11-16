# Build and validate forms

**Goal:** collect input with an HTML `<form>`, let the host check the usual constraints, add your own rules, and read the values.

The renderer implements HTML form behaviour natively: `required`, `type="email"`, `minlength`/`maxlength`, `min`/`max`/`step`, `pattern`, `:invalid` styling, Enter-to-submit (implicit submission), `<button>` submitters and form reset. Your app sees the outcome as events.

## Steps

1. Put labelled controls in a `<form id="...">` and give each a `name`.
2. Subscribe to `submit` on the form. It only arrives when **every** control is valid.
3. For a rule HTML cannot express, set a custom validity message on input (`set_custom_validity(id, message)`; an empty message clears it).
4. Optionally subscribe to `invalid` (sent once per failing control on a submit attempt; it does not bubble) to show your own message. The host focuses the first failing control.
5. Read the values with `form_data(form_id)` (ordered `entries` with `name`, `value`, `kind`; repeated names are kept) or `get_value(id)`, then `reset_form(form_id)` if you want the initial values back.

## Python example

<!-- include: examples/howto/python/signup_form.py -->
```python title="examples/howto/python/signup_form.py"
"""Sign-up form: native HTML form validation plus your own rules, then read the submitted values.

Teaches: required/type/minlength constraints checked by the host, set_custom_validity() for a rule
HTML cannot express (passwords must match), the "invalid" and "submit" events, validity(),
form_data() entries, reset_form(), and labelled controls that assistive technology can name.
Run:     python signup_form.py
Guide:   docs/how-to/forms.md
"""
from nativehtmlkit import Application

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><style>
  body { font: 15px sans-serif; margin: 0; background: #f6f7fb; color: #1d2433; }
  main { max-width: 440px; margin: 0 auto; padding: 24px; }
  label { display: block; margin: 12px 0 4px; font-weight: 600; }
  input, select { width: 100%; box-sizing: border-box; padding: 8px; border: 1px solid #9aa6bf; border-radius: 6px; }
  input:invalid { border-color: #c0392b; }
  .check { display: flex; gap: 8px; align-items: center; margin-top: 12px; font-weight: normal; }
  .check input { width: auto; }
  button { margin-top: 16px; padding: 9px 16px; border: 0; border-radius: 6px; background: #2f6fd0; color: white; }
  #result { margin-top: 16px; padding: 12px; background: #e8f3ea; border-radius: 6px; }
  #result:empty { display: none; }
  #problem { color: #b03224; min-height: 1.2em; }
</style></head>
<body><main>
  <h1>Create an account</h1>
  <form id="signup">
    <label for="email">E-mail</label>
    <input id="email" name="email" type="email" required autocomplete="email">
    <label for="password">Password (at least 8 characters)</label>
    <input id="password" name="password" type="password" required minlength="8">
    <label for="confirm">Repeat password</label>
    <input id="confirm" name="confirm" type="password" required>
    <label for="plan">Plan</label>
    <select id="plan" name="plan"><option value="free">Free</option><option value="team">Team</option></select>
    <label class="check"><input id="terms" name="terms" type="checkbox" value="yes" required> I accept the terms</label>
    <button id="create">Create account</button>
  </form>
  <p id="problem" role="alert"></p>
  <div id="result" role="status"></div>
</main></body></html>"""


def main():
    with Application.start(name="Sign up") as app:
        window = app.open_html(PAGE, title="Sign up", width=520, height=640)
        doc = window.document

        def passwords_changed(_event):
            # A custom validity message makes the field invalid until it is cleared again.
            same = doc.get_value("password") == doc.get_value("confirm")
            doc.set_custom_validity("confirm", "" if same else "The passwords do not match.")

        def invalid(event):
            # Sent once per failing control when a submit is attempted (it does not bubble). The host
            # focuses the first failing control, so report only that one.
            element = event.get("element")
            if (doc.focused_element() or {}).get("element") != element:
                return
            label = {"email": "E-mail", "password": "Password", "confirm": "Repeat password",
                     "terms": "Terms"}.get(element, "A field")
            doc.set_text("problem", f"{label}: {doc.validity(element)['message']}")

        def submitted(_event):
            # "submit" only arrives after every constraint (including the custom one) passed.
            entries = doc.form_data("signup")["entries"]
            values = {entry["name"]: entry["value"] for entry in entries}
            doc.set_text("problem", "")
            doc.set_text("result", f"Welcome, {values['email']}! Plan: {values['plan']}.")
            doc.reset_form("signup")

        doc.on("input", passwords_changed, element="password")
        doc.on("input", passwords_changed, element="confirm")
        doc.on("invalid", invalid)
        doc.on("submit", submitted, element="signup")
        doc.focus("email")
        app.run()


if __name__ == "__main__":
    main()
```
<!-- /include -->

<!-- screenshot: howto-signup-form -->

## PowerShell example

The same form with cmdlets. `set_custom_validity` and `get_validity` have no dedicated cmdlet; `Invoke-NativeHTMLKitDocumentCommand -Operation` runs any documented document operation.

<!-- include: examples/howto/powershell/signup-form.ps1 -->
```powershell title="examples/howto/powershell/signup-form.ps1"
# Sign-up form: native HTML validation plus a custom rule, then read the submitted values (PowerShell).
#
# Teaches: required/type/minlength constraints checked by the host, the set_custom_validity document
#          command (via Invoke-NativeHTMLKitDocumentCommand) for a rule HTML cannot express, the
#          "invalid" and "submit" events, Get-NativeHTMLKitFormData and Reset-NativeHTMLKitForm.
# Run:     pwsh -File signup-form.ps1        (Windows PowerShell 5.1: powershell.exe -File signup-form.ps1)
# Guide:   docs/how-to/forms.md
$ErrorActionPreference = 'Stop'
Import-Module NativeHTMLKit -ErrorAction Stop
$app = Start-NativeHTMLKitScript -Name 'Sign up'

$page = @'
<!doctype html>
<html lang="en"><head><meta charset="utf-8"><style>
  body { font: 15px sans-serif; margin: 0; background: #f6f7fb; color: #1d2433; }
  main { max-width: 440px; margin: 0 auto; padding: 24px; }
  label { display: block; margin: 12px 0 4px; font-weight: 600; }
  input, select { width: 100%; box-sizing: border-box; padding: 8px; border: 1px solid #9aa6bf; border-radius: 6px; }
  input:invalid { border-color: #c0392b; }
  button { margin-top: 16px; padding: 9px 16px; border: 0; border-radius: 6px; background: #2f6fd0; color: white; }
  #problem { color: #b03224; min-height: 1.2em; }
  #result { margin-top: 16px; padding: 12px; background: #e8f3ea; border-radius: 6px; }
  #result:empty { display: none; }
</style></head>
<body><main>
  <h1>Create an account</h1>
  <form id="signup">
    <label for="email">E-mail</label>
    <input id="email" name="email" type="email" required>
    <label for="password">Password (at least 8 characters)</label>
    <input id="password" name="password" type="password" required minlength="8">
    <label for="confirm">Repeat password</label>
    <input id="confirm" name="confirm" type="password" required>
    <label for="plan">Plan</label>
    <select id="plan" name="plan"><option value="free">Free</option><option value="team">Team</option></select>
    <button id="create">Create account</button>
  </form>
  <p id="problem" role="alert"></p>
  <div id="result" role="status"></div>
</main></body></html>
'@

try {
    $window = New-NativeHTMLKitWindow -Application $app -Title 'Sign up' -Width 520 -Height 600
    $doc = Open-NativeHTMLKitHtml -Window $window -Html $page

    $checkPasswords = {
        param($eventObject)
        $same = (Get-NativeHTMLKitValue -Document $doc -Element password) -ceq (Get-NativeHTMLKitValue -Document $doc -Element confirm)
        $message = if ($same) { '' } else { 'The passwords do not match.' }
        $null = Invoke-NativeHTMLKitDocumentCommand -Document $doc -Operation set_custom_validity -Parameters @{ element = 'confirm'; message = $message }
    }
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type input -Element password -Callback $checkPasswords
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type input -Element confirm -Callback $checkPasswords

    # "invalid" is sent once per failing control when a submit is attempted; it does not bubble.
    # The host focuses the first failing control, so only that one is reported.
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type invalid -Callback {
        param($eventObject)
        if ((Get-NativeHTMLKitFocusedElement -Document $doc).element -ne $eventObject.element) { return }
        $validity = Invoke-NativeHTMLKitDocumentCommand -Document $doc -Operation get_validity -Parameters @{ element = $eventObject.element }
        Set-NativeHTMLKitDocumentText -Document $doc -Element problem -Text ("{0}: {1}" -f $eventObject.element, $validity.message)
    }

    # "submit" only arrives after every constraint, including the custom one, passed.
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type submit -Element signup -Callback {
        param($eventObject)
        $values = @{}
        foreach ($entry in @((Get-NativeHTMLKitFormData -Document $doc -Form signup).entries)) { $values[$entry.name] = $entry.value }
        Set-NativeHTMLKitDocumentText -Document $doc -Element problem -Text ''
        Set-NativeHTMLKitDocumentText -Document $doc -Element result -Text ("Welcome, {0}! Plan: {1}." -f $values.email, $values.plan)
        $null = Reset-NativeHTMLKitForm -Document $doc -Form signup
    }

    Set-NativeHTMLKitFocus -Document $doc -Element email
    Set-NativeHTMLKitReady -Application $app
    Wait-NativeHTMLKit -Application $app -UntilShutdown
} finally {
    Close-NativeHTMLKit -Application $app
}
```
<!-- /include -->

## Notes

- A `type="number"` field has a default `step` of 1, so `12.50` is invalid unless you set `step="0.01"` (or `step="any"`). The [expenses tutorial](../tutorials/python-ui-expenses.md) uses a text field and its own parsing instead.
- Validity details: `validity(id)` returns `valid`, the browser-style `flags` (`valueMissing`, `typeMismatch`, ...) and the localised `message`. `check_validity(form_id)` lists invalid controls without submitting.
- Trigger a submit from code with `request_submit(form_id)`; it validates first, exactly like the user pressing Enter.
- **Python UI:** wrap controls in `ui.container("form")`, add a submit button with `ui.element("button", attrs={"type": "submit"}, text=...)`, and `ui.on(form, "submit", ...)` (see the [expenses tutorial](../tutorials/python-ui-expenses.md)). **PowerShell UI** has no form container; validate bound states with a computed value as in the [settings tutorial](../tutorials/powershell-ui-settings.md).
- **CLI:** `nativehtmlkit form --html form.html` shows trusted HTML containing `<form id="nhk-form">` and prints the submitted entries as JSON; see the [CLI reference](https://github.com/nativehtmlkit/nativehtmlkit-cli/blob/main/docs/REFERENCE.md).
