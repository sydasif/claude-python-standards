# Google‑Style Docstrings (PEP 257)

> Owns the docstring standard within the Python standards set. Topic index: [index.md](../index.md).

All public modules, classes, and functions must have Google‑style docstrings.

**Forbidden**: Missing docstrings on public entities; Sphinx/reST or NumPy style.

**Required:** Triple quotes, `Args:` section, `Returns:` section, `Raises:` section for known exceptions, module‑level and class docstrings.

## Example

```python
def fetch_user(user_id: int) -> dict:
    """Fetches a user profile from the database.

    Args:
        user_id: The unique identifier of the user.

    Returns:
        A dictionary containing the user's profile data.

    Raises:
        ValueError: If user_id is negative.
    """
    ...
```

---

## Examples

### Function — before/after

**Before** (no docstring, no contract):

```python
def calc(a, b, op):
    if op == "add":
        return a + b
    if op == "sub":
        return a - b
    raise ValueError("bad op")
```

**After** (Google style, typed, documents the raise):

```python
from typing import Literal

def calc(a: int, b: int, op: Literal["add", "sub"]) -> int:
    """Applies a basic arithmetic operation.

    Args:
        a: The left-hand operand.
        b: The right-hand operand.
        op: Which operation to perform.

    Returns:
        The result of `a op b`.

    Raises:
        ValueError: If `op` is not a supported operation.
    """
    if op == "add":
        return a + b
    if op == "sub":
        return a - b
    raise ValueError(f"unsupported op: {op}")
```

### Class — module-level + class docstring

```python
"""User account management.

Provides the `Account` model and helpers for balance operations.
"""

from dataclasses import dataclass


@dataclass
class Account:
    """A single user's balance-holding account.

    Attributes:
        user_id: Owning user's identifier.
        balance: Current balance in cents.
    """

    user_id: int
    balance: int
```

### What NOT to do

```python
def process(data):
    # reST/Sphinx style and missing Raises — both forbidden
    """Process the data.

    :param data: the input
    :return: the output
    """
    ...
```

Use Google style with `Args:` / `Returns:` / `Raises:` and a `Raises:` section
whenever the function can raise.
