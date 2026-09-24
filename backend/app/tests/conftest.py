import os
import tempfile

# Point the app at a throwaway database before any app module is imported,
# so tests never touch the real data dir.
os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="floortile-test-")
