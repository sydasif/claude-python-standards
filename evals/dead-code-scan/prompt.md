---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Bash, Skill]
---
I think this module has accumulated dead code and stale documentation. Find it.

```python
"""User helpers."""

def _epoch_to_datetime(ms):
    """Convert epoch milliseconds to a datetime.

    Fix: the original blueprint exposed this publicly, then nothing called it.
    """
    return datetime.fromtimestamp(ms / 1000)


def display_name(user: dict) -> str:
    """Return the name to show for a user."""
    return user.get("name") or user.get("email") or "unknown"
```
