import os
from pathlib import Path


def get_project_dir() -> Path:
    """Get the project directory from env vars set by Qwen Code hook runner.

    Qwen Code sets three env vars for hooks: QWEN_PROJECT_DIR, CLAUDE_PROJECT_DIR, GEMINI_PROJECT_DIR.
    All point to the same cwd. We check all three with fallback to cwd().
    """
    for var in ("QWEN_PROJECT_DIR", "CLAUDE_PROJECT_DIR", "GEMINI_PROJECT_DIR"):
        val = os.environ.get(var)
        if val:
            return Path(val)
    return Path.cwd()


def get_log_dir() -> Path:
    """Get the logs directory, creating it if needed."""
    log_dir = get_project_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir
