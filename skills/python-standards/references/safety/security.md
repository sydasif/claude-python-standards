# Python Security Rules

Owns security-specific rules and their unique code (secrets, password hashing, SQL).
General coding rules and the `subprocess` no-shell pattern are kept in
[Conventions — Examples §5](../core/conventions-examples.md#5-subprocessrun-over-ossystem);
the canonical toolchain lists `bandit`/`safety`/`uv-secure` in
[Conventions → Tooling defaults](../core/conventions.md#tooling-defaults).

**Forbidden:**

- Hardcoded secrets
- `eval()` / `exec()` with user input
- Unsanitized SQL (use parameterized queries)
- `pickle` from untrusted sources
- Shell‑injection vectors in `subprocess` calls

**Required:**

- Environment variables for secrets
- Parameterized SQL queries
- Input validation
- bcrypt / Argon2 for passwords
- `secrets` module for cryptographic operations
- `subprocess.run([...], shell=False)`

## Additional Scans

```bash
uv run bandit -r src/         # Static security analysis
uv run safety scan            # Dependency vulnerabilities
uv run uv-secure              # Project dependency security
```

---

## Examples

### Secrets — never hardcode, use env vars

**Before:**

```python
API_KEY = "sk_live_3f9a2b..."  # committed to source control — leaked
requests.get("/api", headers={"Authorization": f"Bearer {API_KEY}"})
```

**After:**

```python
import os

API_KEY = os.environ["API_KEY"]  # injected at runtime; never in VCS
requests.get("/api", headers={"Authorization": f"Bearer {API_KEY}"})
```

### SQL — parameterized queries

**Before** (string interpolation → injection vector):

```python
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

**After** (parameters bound by the driver):

```python
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

### `subprocess` — no shell, list args

The no-shell, list-args pattern (and why) is in
[Conventions — Examples §5](../core/conventions-examples.md#5-subprocessrun-over-ossystem).

### Password hashing — bcrypt/argon2, never plaintext

**Before:**

```python
def store_user(password: str) -> None:
    db.save({"password": password})  # plaintext — catastrophic if leaked
```

**After:**

```python
import bcrypt

def store_user(password: str) -> None:
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    db.save({"password_hash": hashed})

def verify_user(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)
```

Security tests (SQL-injection prevention, auth boundaries) belong in
[testing.md → Security Testing](../safety/testing.md#security-testing).
