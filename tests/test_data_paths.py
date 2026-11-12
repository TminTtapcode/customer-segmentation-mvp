"""Kiểm tra đường dẫn độc lập cwd, cấu hình bên ngoài và không ghi dữ liệu."""
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts.data_paths import PROJECT_ROOT, data_root, observation_path


class DataPathTests(unittest.TestCase):
    def test_default_root_independent_of_working_directory(self):
        with TemporaryDirectory() as folder, patch.dict(os.environ, {"REES46_DATA_ROOT": ""}):
            previous = Path.cwd()
            try:
                os.chdir(folder)
                self.assertEqual(data_root(), (PROJECT_ROOT / "data").resolve())
            finally:
                os.chdir(previous)

    def test_absolute_override(self):
        with TemporaryDirectory() as folder, patch.dict(os.environ, {"REES46_DATA_ROOT": folder}):
            self.assertEqual(data_root(), Path(folder).resolve())

    def test_relative_override_independent_of_working_directory(self):
        with TemporaryDirectory() as folder, patch.dict(os.environ, {"REES46_DATA_ROOT": "../datasets/rees46"}):
            previous = Path.cwd()
            try:
                os.chdir(folder)
                self.assertEqual(data_root(), (PROJECT_ROOT / "../datasets/rees46").resolve())
            finally:
                os.chdir(previous)

    def test_blank_override_uses_default(self):
        with patch.dict(os.environ, {"REES46_DATA_ROOT": "   "}):
            self.assertEqual(data_root(), (PROJECT_ROOT / "data").resolve())

    def test_observation_path_with_external_root(self):
        with TemporaryDirectory() as folder, patch.dict(os.environ, {"REES46_DATA_ROOT": folder}):
            self.assertEqual(observation_path(), Path(folder).resolve() / "cleaned/observation_events.parquet")

    def test_resolving_missing_data_does_not_create_files(self):
        with TemporaryDirectory() as folder:
            missing = Path(folder) / "not-created"
            with patch.dict(os.environ, {"REES46_DATA_ROOT": str(missing)}):
                self.assertFalse(observation_path().exists())
                self.assertFalse(missing.exists())


if __name__ == "__main__":
    unittest.main()
