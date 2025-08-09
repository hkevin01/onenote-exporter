import pathlib
import sys

# Ensure src/ is on sys.path for test discovery and imports
ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
