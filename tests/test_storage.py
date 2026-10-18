"""Tests for JSON persistence and error handling."""
import tempfile
import unittest
from pathlib import Path

from models import Project, Task, User
from utils.storage import StorageError, load_users, save_users


class TestStorage(unittest.TestCase):
    def setUp(self):
        for cls in (User, Project, Task):
            cls.reset_counter()
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = Path(self._tmp.name) / "data.json"

    def test_missing_file_gives_empty_list(self):
        self.assertEqual(load_users(self.path), [])

    def test_save_then_load(self):
        user = User("Alex")
        user.add_project(Project("P")).add_task(Task("t"))
        save_users([user], self.path)
        loaded = load_users(self.path)
        self.assertEqual(loaded[0].to_dict(), user.to_dict())

    def test_malformed_json_raises_storage_error(self):
        self.path.write_text("{not json", encoding="utf-8")
        with self.assertRaises(StorageError):
            load_users(self.path)

    def test_wrong_structure_raises_storage_error(self):
        self.path.write_text('{"users": [{"email": "x"}]}', encoding="utf-8")
        with self.assertRaises(StorageError):
            load_users(self.path)

    def test_save_creates_parent_folder(self):
        nested = Path(self._tmp.name) / "sub" / "data.json"
        save_users([User("Alex")], nested)
        self.assertTrue(nested.exists())

    def test_ids_continue_after_load(self):
        save_users([User("Alex"), User("Sam")], self.path)
        User.reset_counter()
        load_users(self.path)
        self.assertEqual(User("New").id, 3)


if __name__ == "__main__":
    unittest.main()
