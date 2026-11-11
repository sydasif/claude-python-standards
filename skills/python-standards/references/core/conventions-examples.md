# Python Conventions — Before/After Examples

Companion to [Conventions](./conventions.md). The **sole** home for before/after code. Each section below has a stable anchor (`#1`, `#2`, …) that `conventions.md` links to. Edit code here, not in the rule files.

---

## Examples

Before/after for each convention with real Python code.

---

<a id="1-type-discipline"></a>
## 1. Type discipline

**Before**:

```python
def get_user(id):
    user = db.query("SELECT * FROM users WHERE id = %s", (id,))
    return user[0] if user else None
```

**After**:

```python
from __future__ import annotations
from typing import Optional

def get_user(id: int) -> Optional[User]:
    user = db.query("SELECT * FROM users WHERE id = %s", (id,))
    return User.from_row(user[0]) if user else None
```

Or with Python 3.10+ union syntax:

```python
def get_user(id: int) -> User | None:
    ...
```

---

<a id="2-pydantic-v2-for-io"></a>
## 2. Pydantic v2 for I/O

**Before**:

```python
def create_order(data: dict):
    items = data.get("items", [])
    customer_id = data.get("customer_id")
    # ... validation scattered through code
```

**After**:

```python
from pydantic import BaseModel, Field

class CreateOrderRequest(BaseModel):
    items: list[OrderItem] = Field(min_length=1)
    customer_id: int

def create_order(data: CreateOrderRequest) -> Order:
    # data is validated by the type
    ...
```

---

<a id="3-pathlib-over-ospath"></a>
## 3. pathlib over os.path

**Before**:

```python
import os

config_dir = os.path.expanduser("~/.config/myapp")
os.makedirs(config_dir, exist_ok=True)
config_file = os.path.join(config_dir, "settings.json")
if os.path.exists(config_file):
    with open(config_file) as f:
        config = json.load(f)
```

**After**:

```python
from pathlib import Path

config_file = Path.home() / ".config" / "myapp" / "settings.json"
config_file.parent.mkdir(parents=True, exist_ok=True)
if config_file.exists():
    config = json.loads(config_file.read_text())
```

---

<a id="4-dataclasses-for-data-containers"></a>
## 4. dataclasses for data containers

**Before**:

```python
class User:
    def __init__(self, id, email, name, created_at):
        self.id = id
        self.email = email
        self.name = name
        self.created_at = created_at

    def __repr__(self):
        return f"User(id={self.id}, email={self.email})"

    def __eq__(self, other):
        return isinstance(other, User) and self.id == other.id
```

**After**:

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    id: int
    email: str
    name: str
    created_at: datetime
```

---

<a id="5-subprocessrun-over-ossystem"></a>
## 5. subprocess.run over os.system

**Before**:

```python
import os
result = os.system(f"git log -1 {file_path}")
# result is the exit code from `man 2 wait`; not useful directly
```

**After**:

```python
import subprocess

result = subprocess.run(
    ["git", "log", "-1", file_path],
    capture_output=True,
    text=True,
    check=True,
)
print(result.stdout)
```

Note: list of args (not shell string). Avoids shell injection. See also [security.md — subprocess](../safety/security.md#subprocess-no-shell-list-args).

---

<a id="6-match-for-tagged-union-dispatch"></a>
## 6. match for tagged-union dispatch

**Before**:

```python
def process(event):
    if isinstance(event, ClickEvent):
        return handle_click(event.x, event.y)
    elif isinstance(event, KeyEvent):
        return handle_key(event.key)
    elif isinstance(event, ResizeEvent):
        return handle_resize(event.w, event.h)
    else:
        raise ValueError(f"Unknown event: {event}")
```

**After**:

```python
def process(event: Event) -> Result:
    match event:
        case ClickEvent(x=x, y=y):
            return handle_click(x, y)
        case KeyEvent(key=key):
            return handle_key(key)
        case ResizeEvent(w=w, h=h):
            return handle_resize(w, h)
```

---

<a id="7-asyncawait-end-to-end"></a>
## 7. async/await end-to-end

**Before** (mixed):

```python
import requests

async def fetch_data():
    response = requests.get(URL)  # BLOCKING in async context
    return response.json()
```

**After**:

```python
import httpx

async def fetch_data() -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(URL)
        return response.json()
```

---

<a id="8-taskgroup-for-structured-concurrency"></a>
## 8. TaskGroup for structured concurrency

**Before**:

```python
async def fetch_all(urls):
    tasks = [fetch_one(url) for url in urls]
    return await asyncio.gather(*tasks)
# If one fails, gather doesn't cancel siblings cleanly
```

**After** (Python 3.11+):

```python
async def fetch_all(urls: list[str]) -> list[dict]:
    results = []
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch_one(url)) for url in urls]
    return [t.result() for t in tasks]
# TaskGroup cancels siblings on first failure; cleaner shutdown
```

See also [async patterns — TaskGroup](../concurrency/async.md#asynciotaskgroup-311-structured-concurrency).

---

<a id="9-lazy-logging"></a>
## 9. Lazy logging

**Before**:

```python
logger.debug(f"Processing user {user_id} with {len(items)} items")
# String interpolation runs EVEN IF logger.debug is filtered out
```

**After**:

```python
logger.debug("Processing user %s with %d items", user_id, len(items))
# Interpolation only happens if the log level is active
```

---

<a id="10-no-print-in-libraries"></a>
## 10. No print() in libraries

**Before** (in library code):

```python
def import_data(file_path):
    print(f"Loading {file_path}...")
    data = parse(file_path)
    print(f"Loaded {len(data)} records")
    return data
```

**After**:

```python
import logging
logger = logging.getLogger(__name__)

def import_data(file_path: Path) -> list[Record]:
    logger.info("Loading %s", file_path)
    data = parse(file_path)
    logger.info("Loaded %d records", len(data))
    return data
```

CLI scripts can still use print(); library code shouldn't.

---

<a id="11-no-bare-except"></a>
## 11. No bare except

**Before**:

```python
try:
    risky()
except:
    log("Failed")
# Catches KeyboardInterrupt, SystemExit — bad
```

**After**:

```python
try:
    risky()
except Exception as e:
    logger.exception("Failed: %s", e)
```

Or for specific recovery:

```python
try:
    risky()
except ValueError as e:
    handle_value_error(e)
except IOError as e:
    handle_io_error(e)
```

See also [error-handling.md](../safety/error-handling.md).

---

<a id="12-no-mutable-default-arguments"></a>
## 12. No mutable default arguments

**Before**:

```python
def add_item(item, items=[]):
    items.append(item)
    return items
# `items` is shared across all calls — bug factory
```

**After**:

```python
def add_item(item: Item, items: list[Item] | None = None) -> list[Item]:
    if items is None:
        items = []
    items.append(item)
    return items
```

---

<a id="13-literal-over-enum"></a>
## 13. Literal over enum for string-literal sets

**Before**:

```python
from enum import Enum

class Status(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    CLOSED = "closed"

def update(status: Status):
    ...
```

**After** (when you don't need the enum's class behavior):

```python
from typing import Literal

Status = Literal["pending", "active", "closed"]

def update(status: Status) -> None:
    ...
```

Lighter, no runtime cost, type-checker still catches typos.

---

<a id="14-stringly-typed-return--typed-return"></a>
## 14. Stringly-typed return → typed return

**Before**:

```python
def parse_command(s):
    if s.startswith("/"):
        return "command"
    elif s.startswith("@"):
        return "mention"
    else:
        return "text"
# Caller has to remember the exact strings; no help from the type-checker
```

**After**:

```python
from typing import Literal

CommandKind = Literal["command", "mention", "text"]

def parse_command(s: str) -> CommandKind:
    if s.startswith("/"):
        return "command"
    elif s.startswith("@"):
        return "mention"
    return "text"
```

---

<a id="15-canonical-tool-configuration"></a>
## 15. Canonical ruff configuration & project bootstrap

The single source of truth for `pyproject.toml` and the ruff config is
**[Conventions → Canonical tool configuration](./conventions.md#canonical-tool-configuration)**.

Edit it there — do not maintain a copy here. Run:

```bash
ruff check . --fix && ruff format .
```

---

<a id="16-functions-over-classes"></a>
## 16. Functions over classes

**Before**:

```python
class PriceCalculator:
    def __init__(self, tax_rate):
        self.tax_rate = tax_rate

    def total(self, subtotal):
        return subtotal * (1 + self.tax_rate)

total = PriceCalculator(0.2).total(100)
```

**After**:

```python
def total_with_tax(subtotal: float, tax_rate: float) -> float:
    return subtotal * (1 + tax_rate)

total = total_with_tax(100, 0.2)
```

Keep a class when it holds real state or is required by a framework — not as a namespace for one method.
