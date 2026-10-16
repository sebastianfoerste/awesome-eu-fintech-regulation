"""Make scripts/ importable, so the tests can exercise the Level 2 and CELLAR scripts offline."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
