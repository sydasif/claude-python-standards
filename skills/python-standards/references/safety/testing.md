# Python Testing Standards

> Owns testing standards. `pytest` is the chosen runner per [Conventions → Tooling defaults](../core/conventions.md#tooling-defaults); the run commands in [style-toolchain.md → Standard Workflow](../core/style-toolchain.md#standard-workflow).

Use pytest. AAA pattern. Tests fully independent. No shared mutable state.
Coverage targets: business logic ≥95%, APIs ≥90%, models ≥85%.
All existing tests must pass before you make any changes.

---

## Pre-Change Gate

Existing tests must pass before changes. Document existing failures; do not treat them as regressions.

## Every Task Requires

- [ ] Static checks pass (lint + types)
- [ ] Positive test case (expected behavior)
- [ ] Negative test case (bad/edge input)
- [ ] Regression tests still pass

## Coverage Thresholds (branch coverage)

| Scope          | Minimum Target |
| -------------- | -------------- |
| Business logic | ≥ 95%          |
| APIs           | ≥ 90%          |
| Models         | ≥ 85%          |

These are targets, not hard gates. When below thresholds, note the gap.

## Test Authoring Rules

- Follow **AAA pattern**: Arrange → Act → Assert
- Tests are fully **independent** — no shared mutable state
- No test chaining; no flaky tests; minimize mocking
- Never delete, weaken, or skip a test to make a diff pass — surface the failure instead

## Test Organization

- Place tests in `tests/` directory
- Mirror source structure: `src/module.py` → `tests/test_module.py`
- Use descriptive names: `test_calculate_total_with_discount()`
- Write tests as plain functions; group related ones by shared name prefix (`test_calculator_add_*`) or by file, and share setup via fixtures — avoid `Test*` classes

## Test Patterns

### Basic Unit Test

```python
def test_addition():
    assert add(2, 3) == 5
```

### Parametrized Test

```python
@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (-1, 1, 0),
])
def test_addition_parametrized(a, b, expected):
    assert add(a, b) == expected
```

### Property-Based Test

```python
from hypothesis import given, strategies as st

@given(st.integers(), st.integers())
def test_addition_commutative(a, b):
    assert add(a, b) == add(b, a)
```

### Test with Fixture

```python
@pytest.fixture
def sample_orders() -> list[dict[str, float]]:
    return [{"price": 10.0}, {"price": 5.5}]

def test_total_of_orders(sample_orders):
    assert total(sample_orders) == 15.5
```

### Error Condition Testing

```python
def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(5, 0)
```

---

## Examples — positive, negative, edge

### AAA explained (Arrange → Act → Assert)

**Before** (mixed steps, unclear what is being tested):

```python
def test_discount():
    c = Cart()
    c.add(Item(price=100))
    c.add_coupon("SAVE10")
    assert c.total() == 90
```

**After** (each phase is explicit):

```python
def test_discount_applies_ten_percent():
    # Arrange
    cart = Cart()
    cart.add(Item(price=100))
    cart.add_coupon("SAVE10")

    # Act
    total = cart.total()

    # Assert
    assert total == 90
```

### Negative test — bad input raises

```python
def test_add_rejects_negative_quantity():
    cart = Cart()
    with pytest.raises(ValueError, match="quantity must be >= 0"):
        cart.add(Item(price=10), quantity=-1)
```

### Edge case — empty input

```python
def test_total_of_empty_cart_is_zero():
    assert Cart().total() == 0
```

### Mirrored file + fixture reuse

```python
# tests/test_cart.py  (mirrors src/cart.py)
import pytest

from app.cart import Cart, Item


@pytest.fixture
def cart() -> Cart:
    return Cart()


def test_add_increases_line_count(cart: Cart) -> None:
    cart.add(Item(price=5))
    assert len(cart.lines) == 1
```

## Security Testing

- Test SQL injection prevention (parameterized queries)
- Test unauthorized access returns 401/403
- Validate input sanitization
- Test authentication/authorization boundaries

## Commands

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-branch --cov-fail-under=85

# Run specific test file
uv run pytest tests/test_module.py

# Run specific test function
uv run pytest tests/test_module.py::test_function_name

# Show missing coverage lines
uv run pytest --cov=src --cov-report=term-missing

# Run with verbose output
uv run pytest -v

# Generate HTML coverage report
uv run pytest --cov=src --cov-report=html
```

## Best Practices

- **Naming**: `test_` prefix, descriptive names, include expected outcome
- **Structure**: AAA pattern — Arrange, Act, Assert
- **Isolation**: Each test independent, use fixtures, no shared mutable state
- **Documentation**: Docstrings for complex test cases, explain edge case importance
- **Coverage**: Track gaps with `--cov-report=term-missing` and address them
- **Security**: Mock sensors and API clients for integration testing
