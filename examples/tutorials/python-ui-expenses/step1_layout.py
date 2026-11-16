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
