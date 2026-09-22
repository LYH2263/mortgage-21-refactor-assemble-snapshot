import os
import tempfile

os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="mortgage-test-"))

import pytest
from app import seed


@pytest.fixture(scope="session", autouse=True)
def _init_db():
    seed.init_db()
