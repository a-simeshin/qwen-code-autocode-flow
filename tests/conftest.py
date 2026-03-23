from pathlib import Path

import pytest


@pytest.fixture
def qwen_dir() -> Path:
    """Return the path to the .qwen directory relative to the project root."""
    return Path(__file__).parent.parent / ".qwen"
