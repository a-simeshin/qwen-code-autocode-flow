#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///

import json
import sys
from datetime import datetime

from utils.paths import get_log_dir

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


def debug_log(message: str) -> None:
    """Write debug message to logs/subagent_debug.log"""
    try:
        log_dir = get_log_dir()
        debug_path = log_dir / "subagent_debug.log"
        timestamp = datetime.now().isoformat()
        with open(debug_path, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass


def main() -> None:
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        # Extract required fields (used for logging context)
        session_id = input_data.get("session_id", "")
        stop_hook_active = input_data.get("stop_hook_active", False)

        # Ensure log directory exists
        log_dir = get_log_dir()

        # Log subagent stop event
        log_path = log_dir / "subagent_stop.json"

        # Read existing log data or initialize empty list
        if log_path.exists():
            with open(log_path, 'r') as f:
                try:
                    log_data = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    log_data = []
        else:
            log_data = []

        # Add timestamp and append
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "agent_id": input_data.get("agent_id", "unknown"),
            "stop_hook_active": stop_hook_active,
            "raw_input": input_data,
        }
        log_data.append(log_entry)

        # Write back to file with formatting
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)

        debug_log(f"Subagent stop logged for agent: {input_data.get('agent_id', 'unknown')}")

        sys.exit(0)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)


if __name__ == "__main__":
    main()
