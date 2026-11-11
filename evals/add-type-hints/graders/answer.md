---
type: llm
---
PASS if the reply contains a rewritten `total` function with an annotated
parameter (`items: ...`) and an annotated return type, and keeps the same
behaviour (summing item prices).
FAIL if the function is left unannotated, the behaviour changes, or the reply
only describes what to change without showing the code.
