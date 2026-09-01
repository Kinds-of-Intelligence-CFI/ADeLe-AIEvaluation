"""Put this lab folder on sys.path so `import rivercross` resolves when running
`pytest labs/rivercross`. The river-crossing testbed is scratch (not part of the
shipped `adele` package); see README.md."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
