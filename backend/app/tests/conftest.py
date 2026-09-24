import os
import tempfile

# Point the app at a throwaway database before any app module is imported.
os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="floortile-test-")

from app import seed  # noqa: E402

seed.init_db()
