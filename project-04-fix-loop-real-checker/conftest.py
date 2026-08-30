"""Pytest config: makes the project root importable so tests can find the
buggy_math module without packaging it as an installable package.

This is a test scaffolding concern; in a real project you'd use a proper
package layout (src/, pyproject.toml, etc.) and wouldn't need this file.
"""

import sys
from pathlib import Path

# Add the project root to sys.path so `import buggy_math` works.
sys.path.insert(0, str(Path(__file__).parent))
