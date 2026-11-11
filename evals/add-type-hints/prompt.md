---
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---
Add type hints to this function and modernize it to current Python:

```python
def total(items):
    result = 0
    for i in items:
        result = result + i["price"]
    return result
```
