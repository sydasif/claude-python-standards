# Common Refactoring Scenarios

## Scenario 1: Migrate to f-strings

```python
# Before
msg = "Host %s unreachable after %d retries" % (host, retries)
msg = "Host {} unreachable after {} retries".format(host, retries)

# After
msg = f"Host {host} unreachable after {retries} retries"

# Preserve alignment options where needed
msg = f"{'Interface':<20} {'Status':>10}"
```

## Scenario 2: Migrate to dataclasses

```python
# Before
class DeviceInfo:
    def __init__(self, hostname, ip, platform):
        self.hostname = hostname
        self.ip = ip
        self.platform = platform

    def __repr__(self):
        return f"DeviceInfo({self.hostname}, {self.ip}, {self.platform})"

# After
from dataclasses import dataclass

@dataclass
class DeviceInfo:
    hostname: str
    ip: str
    platform: str
```

## Scenario 3: Migrate to pathlib

```python
# Before
import os
config_path = os.path.join(base_dir, "config", "devices.yaml")
if os.path.exists(config_path):
    with open(config_path) as f:
        ...

# After
from pathlib import Path
config_path = Path(base_dir) / "config" / "devices.yaml"
if config_path.exists():
    with config_path.open() as f:
        ...
```

## Scenario 4: Migrate to match statements (Python 3.10+ only)

```python
# Before
if platform == "ios":
    driver = IOSDriver()
elif platform == "eos":
    driver = EOSDriver()
elif platform == "nxos":
    driver = NXOSDriver()
else:
    raise ValueError(f"Unknown platform: {platform}")

# After (Python 3.10+)
match platform:
    case "ios":
        driver = IOSDriver()
    case "eos":
        driver = EOSDriver()
    case "nxos":
        driver = NXOSDriver()
    case _:
        raise ValueError(f"Unknown platform: {platform}")
```

## Scenario 5: Replace print with logging (behavior change - confirm first)

```python
# Before
print(f"Connecting to {host}...")
print(f"ERROR: timeout on {host}")

# After
import logging
logger = logging.getLogger(__name__)

logger.debug("Connecting to %s", host)
logger.error("Timeout on %s", host)
```

> **Why `%`-style args in logging, not f-strings?** The logging module uses lazy formatting - the string is only interpolated if the log level is actually active. With f-strings, the interpolation happens unconditionally at the call site, even if the message is never emitted. Use `%`-style positional args (`"msg %s", value`) in all `logger.*` calls.

> **Where do the calls go?** In orchestration or effect code, not inside pure functions (see the function-first-refactor skill). A pure function returns data or raises; its caller logs.
