# Extended Example: Order Submission

## Before: tightly coupled

```python
def handle_order_submission(order_data):
    if not validate_order(order_data):
        raise ValueError("Invalid order")

    db.save_order(order_data)
    invoice = generate_invoice(order_data)
    pdf = create_pdf(invoice)
    send_email_with_attachment(order_data["user_email"], pdf)
```

Problems: validation, persistence, invoice building, PDF rendering, and email are all in one function, so testing the invoice logic requires a database and mail server, and the invoice can't be reused for downloads or previews.

## After: layered

```python
# --- core logic (pure) ---
def is_order_valid(order_data): ...
def build_invoice(order_data): ...
def render_invoice_pdf(invoice): ...   # returns bytes, no file or network I/O

# --- side effects ---
def send_invoice_email(email, pdf):
    smtp.send(...)

# --- orchestration ---
def process_order(order_data):
    if not is_order_valid(order_data):
        raise ValueError("Invalid order")

    db.save_order(order_data)
    invoice = build_invoice(order_data)
    pdf = render_invoice_pdf(invoice)
    send_invoice_email(order_data["user_email"], pdf)
```

The order of effects is unchanged: validate, save, build, render, send.

## Resulting benefits

- `build_invoice` is reusable for downloads, previews, printing, and exports.
- Core logic is unit tested with plain inputs and outputs: no DB, no SMTP.
- The email transport can be swapped later with no impact on business rules.

## Matching tests

```python
# Pure core: no mocks
def test_build_invoice_totals():
    order = {"items": [{"price": 10, "qty": 2}, {"price": 5, "qty": 1}]}
    assert build_invoice(order)["total"] == 25

# Orchestration: mock only the effects, use the real validator
def test_process_order_rejects_invalid_and_saves_nothing(mocker):
    save = mocker.patch("orders.db.save_order")
    send = mocker.patch("orders.send_invoice_email")
    with pytest.raises(ValueError):
        process_order({})
    save.assert_not_called()
    send.assert_not_called()
```

Note the orchestration test does not patch `is_order_valid`. Patching a pure function to force a branch is a sign the layers are tangled; feed it real invalid data instead.
