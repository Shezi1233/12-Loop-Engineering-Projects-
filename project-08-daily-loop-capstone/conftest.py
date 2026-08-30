"""Pytest config: makes the project root importable so tests can find the
target module without packaging it.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
