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
