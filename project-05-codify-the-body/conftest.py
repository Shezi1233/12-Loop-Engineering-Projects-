"""Pytest config: makes the project root importable so tests can find the
buggy_math module without packaging it as an installable package.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
