from pathlib import Path
import json
import os
import tempfile

server_log_path = Path("data/server.log")
server_pid_path = Path("data/server.pid")
auth_path = Path("data/auth.json")


def secure_data_dir() -> None:
    """Create the local state directory with owner-only permissions."""
    auth_path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    os.chmod(auth_path.parent, 0o700)


def save_storage_state(context) -> None:
    """Persist browser state only after securing its directory and file."""
    secure_data_dir()
    fd, temporary = tempfile.mkstemp(prefix=".auth-", suffix=".tmp", dir=auth_path.parent)
    os.fchmod(fd, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(context.storage_state(), stream, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, auth_path)
        os.chmod(auth_path, 0o600)
    except Exception:
        try:
            os.close(fd)
        except OSError:
            pass
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise
