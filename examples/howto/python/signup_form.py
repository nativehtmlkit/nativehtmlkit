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
