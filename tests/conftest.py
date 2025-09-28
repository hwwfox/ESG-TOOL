"""Test configuration for the simplified ESG tool package."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the repository root (containing the ``esg_tool`` package) is importable
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
