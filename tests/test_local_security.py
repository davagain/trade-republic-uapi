import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from trade_republic_uapi.paths import save_storage_state
from trade_republic_uapi import api_server


class FakeContext:
    def __init__(self):
        self.paths = []

    def storage_state(self):
        self.paths.append("called")
        return {"cookies": []}


class FailingContext:
    def storage_state(self):
        raise RuntimeError("browser unavailable")


class LocalSecurityTest(unittest.TestCase):
    def test_storage_state_secures_directory_and_file(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "nested" / "auth.json"
            context = FakeContext()
            with patch("trade_republic_uapi.paths.auth_path", target):
                save_storage_state(context)
            self.assertEqual(context.paths, ["called"])
            self.assertEqual(os.stat(target.parent).st_mode & 0o777, 0o700)
            self.assertEqual(os.stat(target).st_mode & 0o777, 0o600)

    def test_directory_is_secured_before_browser_state_is_requested(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "nested" / "auth.json"

            class InspectingContext:
                def storage_state(self):
                    self.mode = os.stat(target.parent).st_mode & 0o777
                    return {"cookies": []}

            context = InspectingContext()
            with patch("trade_republic_uapi.paths.auth_path", target):
                save_storage_state(context)
            self.assertEqual(context.mode, 0o700)

    def test_failed_refresh_preserves_previous_state_and_leaves_no_temp(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "nested" / "auth.json"
            target.parent.mkdir(mode=0o700)
            target.write_text('{"cookies": ["old"]}')
            with patch("trade_republic_uapi.paths.auth_path", target):
                with self.assertRaisesRegex(RuntimeError, "browser unavailable"):
                    save_storage_state(FailingContext())
            self.assertEqual(target.read_text(), '{"cookies": ["old"]}')
            self.assertEqual(list(target.parent.glob(".auth-*.tmp")), [])

    def test_server_binds_loopback_only(self):
        with patch.object(api_server.uvicorn, "run") as run:
            api_server.start_api_server(8765)
        run.assert_called_once_with(api_server.app, host="127.0.0.1", port=8765, log_level="warning")

    def test_failed_publish_preserves_previous_state_and_cleans_temp(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "auth.json"
            target.write_text('{"cookies": ["old"]}')
            with patch("trade_republic_uapi.paths.auth_path", target), patch(
                "trade_republic_uapi.paths.os.replace", side_effect=OSError("publish failed")
            ):
                with self.assertRaisesRegex(OSError, "publish failed"):
                    save_storage_state(FakeContext())
            self.assertEqual(target.read_text(), '{"cookies": ["old"]}')
            self.assertEqual(list(target.parent.glob(".auth-*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
