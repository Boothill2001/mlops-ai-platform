import sys
from pathlib import Path

# Ensure both backend/ and project root are on sys.path
_backend = Path(__file__).resolve().parent.parent
_root = _backend.parent

for p in (_backend, _root):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
