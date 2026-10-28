"""Start Ghostlet. Used for `python run_ghostlet.py` and as the PyInstaller entry script."""
import sys

from ghostlet.app import main

if __name__ == "__main__":
    sys.exit(main())
