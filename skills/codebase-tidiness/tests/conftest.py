"""Put ``scripts/`` on the path so the tests can import the scan script."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
