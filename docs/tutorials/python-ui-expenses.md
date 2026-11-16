# Tutorial: an expense tracker with computed totals (Python UI)

You will build **Expenses** with the `nativehtmlkit_ui` component library: a form to add expenses, a list of entries, totals per category that update by themselves, and a JSON file that is saved whenever the data changes. You will not write any HTML.

<!-- screenshot: tutorial-python-ui-expenses -->

**Time:** about 30 minutes. **You need:** `nativehtmlkit_ui` installed and the counter from [Python UI in five minutes](../getting-started/python-ui.md) working. Final code: [`examples/tutorials/python-ui-expenses/expenses.py`](https://github.com/nativehtmlkit/nativehtmlkit/blob/main/examples/tutorials/python-ui-expenses/expenses.py).

## Step 1: a reactive form

<!-- include: examples/tutorials/python-ui-expenses/step1_layout.py -->
```python title="examples/tutorials/python-ui-expenses/step1_layout.py"
"""Expense tracker tutorial, step 1: a reactive form with nativehtmlkit_ui.

Teaches: state(), two-way inputs (ui.input, ui.select), a text bound to a lambda that re-renders
whenever the states it reads change, cards/rows/columns.
Run:     python step1_layout.py
Guide:   docs/tutorials/python-ui-expenses.md (step 1 of 3)
"""
from nativehtmlkit import Application
from nativehtmlkit_ui import UI, state

CATEGORIES = [("food", "Food"), ("travel", "Travel"), ("home", "Home"), ("other", "Other")]


def main():
    with Application.start(name="Expenses") as app:
        description = state("")
        amount = state("")
        category = state("food")

        ui = UI(title="Expenses", theme="daylight", density="regular", width=640, height=560)
        with ui.column():
            ui.heading("Expenses", level=1)
            with ui.card():
                ui.heading("New expense", level=2)
                ui.input(description, label="Description", placeholder="Coffee with Sam")
                with ui.row():
                    ui.input(amount, label="Amount", placeholder="0.00")
                    ui.select(category, CATEGORIES, label="Category")
                ui.text(lambda: f"Preview: {description.value or '(no description)'} - "
                                f"{amount.value or '0'} ({category.value})", muted=True)
        try:
            ui.mount(app)
            app.run()
        finally:
            ui.dispose()


if __name__ == "__main__":
    main()
```
<!-- /include -->

Run `python step1_layout.py` and type into the fields: the preview line follows every keystroke.

- `state("")` creates an observable value. `ui.input(description, label=...)` is **two-way**: typing updates the state, and setting the state updates the field.
- `ui.select(category, CATEGORIES, ...)` takes `(value, label)` pairs and binds the selected value.
- `ui.text(lambda: ...)` binds a text to an expression. The library records which states the lambda reads (`description`, `amount`, `category`) and re-evaluates it when one of them changes.
- `with ui.column():`, `ui.row()` and `ui.card()` arrange components. The whole tree is built before `ui.mount(app)`; after mounting you change state, not structure.
- The amount is a plain text field on purpose. A `kind="number"` field would apply the browser rule `step="1"`, so the host's form validation would reject `12.50`. The app validates the amount itself in the next step.

## Step 2: validate and add

<!-- include: examples/tutorials/python-ui-expenses/step2_add.py -->
```python title="examples/tutorials/python-ui-expenses/step2_add.py"
"""Expense tracker tutorial, step 2: validate input and add expenses to a list.

Teaches: a <form> container with a real submit button (Enter or click both submit), the "submit"
event via ui.on(), validation with Decimal, a bound error message, ui.text_list() with a formatter.
Run:     python step2_add.py
Guide:   docs/tutorials/python-ui-expenses.md (step 2 of 3)
"""
from decimal import Decimal, InvalidOperation

from nativehtmlkit import Application
from nativehtmlkit_ui import UI, state

CATEGORIES = [("food", "Food"), ("travel", "Travel"), ("home", "Home"), ("other", "Other")]
LABELS = dict(CATEGORIES)


def parse_amount(text):
    """Return a positive Decimal with two places, or None."""
    try:
        value = Decimal(text.strip())
    except InvalidOperation:
        return None
    if not value.is_finite() or value <= 0 or value > Decimal("1000000"):
        return None
    return value.quantize(Decimal("0.01"))


def describe(expense):
    return f"{expense['description']} - {LABELS[expense['category']]} - {expense['amount']}"


def main():
    with Application.start(name="Expenses") as app:
        description = state("")
        amount = state("")
        category = state("food")
        expenses = state([])
        error = state("")

        def add(_event):
            value = parse_amount(amount.value)
            if not description.value.strip():
                error.set("Enter a description.")
            elif value is None:
                error.set("Enter an amount greater than 0, for example 12.50.")
            else:
                entry = {"description": description.value.strip(), "amount": str(value),
                         "category": category.value}
                expenses.set([*expenses.value, entry])  # assign a new list: state is not a deep proxy
                description.set("")
                amount.set("")
                error.set("")

        ui = UI(title="Expenses", theme="daylight", density="regular", width=640, height=620)
        with ui.column():
            ui.heading("Expenses", level=1)
            with ui.card():
                with ui.container("form") as form:
                    ui.input(description, label="Description", placeholder="Coffee with Sam")
                    with ui.row():
                        ui.input(amount, label="Amount", placeholder="0.00")
                        ui.select(category, CATEGORIES, label="Category")
                    ui.element("button", css_class="nhk-button nhk-primary", attrs={"type": "submit"},
                               text="Add expense")
                ui.on(form, "submit", add)
                ui.text(error)
            with ui.card():
                ui.heading("This month", level=2)
                ui.text_list(expenses, formatter=describe)
        try:
            ui.mount(app)
            app.run()
        finally:
            ui.dispose()


if __name__ == "__main__":
    main()
```
<!-- /include -->

- `ui.container("form")` puts the fields in a real `<form>`. `ui.element("button", attrs={"type": "submit"}, ...)` adds a submit button, so both **Enter** and a click submit the form, and `ui.on(form, "submit", add)` receives it. (`ui.button()` creates `type="button"` buttons, which never submit a form.)
- `parse_amount()` uses `Decimal`, never `float`, for money, and accepts only positive amounts.
- Validation results are state too: `error.set(...)` shows a message through `ui.text(error)`.
- `expenses.set([*expenses.value, entry])` assigns a **new list**. State compares values to decide whether anything changed; mutating the existing list in place would not notify anyone.
- `ui.text_list(expenses, formatter=describe)` renders one escaped `<li>` per entry.

## Step 3: totals, actions and saving

<!-- include: examples/tutorials/python-ui-expenses/expenses.py -->
```python title="examples/tutorials/python-ui-expenses/expenses.py"
"""Expenses: an expense tracker with computed totals, built with nativehtmlkit_ui (tutorial final code).

Teaches: state() and computed() values, a validated <form> with a submit button, bound text, badges,
lists and conditional regions, buttons that change state, and saving state to a JSON file whenever
it changes (State.subscribe).
Run:     python expenses.py [EXPENSES_FILE]
         (default file: .nativehtmlkit-expenses.json in your home directory)
Guide:   docs/tutorials/python-ui-expenses.md (step 3 of 3)
"""
import json
import os
import sys
import tempfile
from decimal import Decimal, InvalidOperation
from pathlib import Path

from nativehtmlkit import Application
from nativehtmlkit_ui import UI, computed, state

CATEGORIES = [("food", "Food"), ("travel", "Travel"), ("home", "Home"), ("other", "Other")]
LABELS = dict(CATEGORIES)


def parse_amount(text):
    """Return a positive Decimal with two places, or None."""
    try:
        value = Decimal(text.strip())
    except InvalidOperation:
        return None
    if not value.is_finite() or value <= 0 or value > Decimal("1000000"):
        return None
    return value.quantize(Decimal("0.01"))


def describe(expense):
    return f"{expense['description']} - {LABELS.get(expense['category'], 'Other')} - {expense['amount']}"


def load(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []
    return [{"description": str(e["description"]), "amount": str(parse_amount(str(e["amount"])) or "0.00"),
             "category": e["category"] if e["category"] in LABELS else "other"}
            for e in data.get("expenses", [])]


def save(path, expenses):
    fd, temporary = tempfile.mkstemp(prefix=".expenses-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump({"version": 1, "expenses": expenses}, stream, indent=2)
        os.replace(temporary, path)
    except BaseException:
        os.unlink(temporary)
        raise


def main():
    with Application.start(name="Expenses") as app:
        path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".nativehtmlkit-expenses.json"
        description = state("")
        amount = state("")
        category = state("food")
        error = state("")
        try:
            expenses = state(load(path))
        except (OSError, ValueError, KeyError, TypeError) as problem:
            expenses = state([])
            error.set(f"Could not read {path.name}: {problem}")

        total = computed(lambda: sum((Decimal(e["amount"]) for e in expenses.value), Decimal("0.00")))
        by_category = computed(lambda: [
            f"{label}: {sum((Decimal(e['amount']) for e in expenses.value if e['category'] == key), Decimal('0.00'))}"
            for key, label in CATEGORIES])

        def persist():
            try:
                save(path, expenses.value)
            except OSError as problem:
                error.set(f"Not saved: {problem.strerror}")
        expenses.subscribe(persist)

        def add(_event):
            value = parse_amount(amount.value)
            if not description.value.strip():
                error.set("Enter a description.")
            elif value is None:
                error.set("Enter an amount greater than 0, for example 12.50.")
            else:
                entry = {"description": description.value.strip(), "amount": str(value), "category": category.value}
                expenses.set([*expenses.value, entry])
                description.set("")
                amount.set("")
                error.set("")

        ui = UI(title="Expenses", theme="daylight", density="regular", width=700, height=680)
        with ui.column():
            ui.heading("Expenses", level=1)
            with ui.row():
                ui.badge(lambda: f"Total {total.value}")
                ui.badge(lambda: f"{len(expenses.value)} entries")
            with ui.grid():
                with ui.card():
                    ui.heading("New expense", level=2)
                    with ui.container("form") as form:
                        ui.input(description, label="Description", placeholder="Coffee with Sam")
                        ui.input(amount, label="Amount", placeholder="0.00")
                        ui.select(category, CATEGORIES, label="Category")
                        ui.element("button", css_class="nhk-button nhk-primary", attrs={"type": "submit"},
                                   text="Add expense")
                    ui.on(form, "submit", add)
                    with ui.when(lambda: bool(error.value)):
                        ui.alert(error)
                with ui.card():
                    ui.heading("By category", level=2)
                    ui.text_list(by_category)
            with ui.card():
                ui.heading("Entries", level=2)
                with ui.when(lambda: not expenses.value):
                    ui.text("No expenses yet. Add your first one above.", muted=True)
                ui.text_list(expenses, formatter=describe)
                with ui.row():
                    ui.button("Remove last", variant="secondary",
                              on_click=lambda _e: expenses.set(expenses.value[:-1]))
                    ui.button("Clear all", variant="danger", on_click=lambda _e: expenses.set([]))
        try:
            ui.mount(app)
            app.run()
        finally:
            ui.dispose()
            total.close()
            by_category.close()


if __name__ == "__main__":
    main()
```
<!-- /include -->

- `computed(lambda: ...)` derives a value from states and recomputes when they change. `total` and `by_category` read `expenses.value`, so adding an entry updates the badge and the category list automatically.
- `with ui.when(lambda: bool(error.value)):` shows its contents only while the condition is true. The region stays mounted and is hidden with a CSS class, so inputs inside keep their state.
- `ui.button("Clear all", variant="danger", on_click=...)` changes state from a click; the list and totals follow.
- `expenses.subscribe(persist)` calls `persist()` after every change, which writes the file atomically (temporary file, then `os.replace`). The path is the first command-line argument or `.nativehtmlkit-expenses.json` in your home folder.
- In `finally`, `ui.dispose()` releases the UI, and each `computed` is closed.

!!! note "Threads and computed values"
    All changes in this app happen in UI event callbacks. If you update states from worker threads, avoid `computed()` values whose dependencies are changed by several threads at the same time: UI 0.1.1 has a known race there ([limitations](../capabilities/limitations.md)). See [Background work](../how-to/background-work.md) for a safe pattern.

## What you learned

- `state()`, `computed()` and bindings replace manual page updates.
- Two-way inputs, selects, conditional regions and text lists.
- A real `<form>` with a submit button inside the UI library, and your own validation.
- Persisting state whenever it changes.

## Where next

- [Theme the UI library](../how-to/theming-ui.md): themes, densities and an accent colour.
- [Native file dialogs](../how-to/file-dialogs.md): let the user choose where to save, using the SDK next to the UI.
- [UI API reference](https://github.com/nativehtmlkit/nativehtmlkit_ui/blob/main/docs/API.md).
