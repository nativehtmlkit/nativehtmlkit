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
