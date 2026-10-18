"""End-to-end tests for the CLI, using a temporary data file."""
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import main as cli
from models import Project, Task, User
from utils.storage import load_users


class TestCLI(unittest.TestCase):
    def setUp(self):
        for cls in (User, Project, Task):
            cls.reset_counter()
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = str(Path(self._tmp.name) / "data.json")

    def run_cli(self, *args):
        """Run the CLI; return (exit_code, stdout, stderr)."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(["--data-file", self.path, *args])
        return code, out.getvalue(), err.getvalue()

    def seed(self):
        self.run_cli("add-user", "--name", "Alex")
        self.run_cli("add-project", "--user", "Alex", "--title", "CLI Tool")
        self.run_cli("add-task", "--project", "CLI Tool", "--title", "Implement add-task")

    def test_add_user_and_list(self):
        self.assertEqual(self.run_cli("add-user", "--name", "Alex")[0], 0)
        code, out, _ = self.run_cli("list-users")
        self.assertEqual(code, 0)
        self.assertIn("Alex", out)

    def test_duplicate_user_fails(self):
        self.run_cli("add-user", "--name", "Alex")
        code, _, err = self.run_cli("add-user", "--name", "alex")
        self.assertEqual(code, 1)
        self.assertIn("already exists", err)

    def test_project_for_unknown_user_fails(self):
        code, _, err = self.run_cli("add-project", "--user", "Ghost", "--title", "X")
        self.assertEqual(code, 1)
        self.assertIn("not found", err)

    def test_full_workflow_persists(self):
        self.seed()
        code, _, _ = self.run_cli(
            "complete-task", "--project", "CLI Tool", "--title", "Implement add-task"
        )
        self.assertEqual(code, 0)
        task = load_users(self.path)[0].projects[0].tasks[0]
        self.assertEqual(task.status, "complete")

    def test_list_projects_for_user(self):
        self.seed()
        code, out, _ = self.run_cli("list-projects", "--user", "Alex")
        self.assertEqual(code, 0)
        self.assertIn("CLI Tool", out)

    def test_search_projects(self):
        self.seed()
        _, out, _ = self.run_cli("search-projects", "--keyword", "cli")
        self.assertIn("CLI Tool", out)
        _, out, _ = self.run_cli("search-projects", "--keyword", "zzz")
        self.assertNotIn("CLI Tool", out)

    def test_bad_date_rejected(self):
        self.run_cli("add-user", "--name", "Alex")
        code, _, err = self.run_cli(
            "add-project", "--user", "Alex", "--title", "P", "--due-date", "tomorrow"
        )
        self.assertEqual(code, 1)
        self.assertIn("YYYY-MM-DD", err)

    def test_assigning_to_unknown_user_fails(self):
        self.seed()
        code, _, _ = self.run_cli(
            "add-task", "--project", "CLI Tool", "--title", "T2", "--assigned-to", "Ghost"
        )
        self.assertEqual(code, 1)

    def test_update_task_status(self):
        self.seed()
        code, _, _ = self.run_cli(
            "update-task", "--project", "CLI Tool",
            "--title", "Implement add-task", "--status", "in-progress",
        )
        self.assertEqual(code, 0)
        task = load_users(self.path)[0].projects[0].tasks[0]
        self.assertEqual(task.status, "in-progress")

    def test_corrupt_data_file_reports_error(self):
        Path(self.path).write_text("oops", encoding="utf-8")
        code, _, err = self.run_cli("list-users")
        self.assertEqual(code, 1)
        self.assertIn("not valid JSON", err)

    def test_duplicate_project_titles_need_user_flag(self):
        for name in ("Alex", "Sam"):
            self.run_cli("add-user", "--name", name)
            self.run_cli("add-project", "--user", name, "--title", "Shared")
        code, _, err = self.run_cli("add-task", "--project", "Shared", "--title", "T")
        self.assertEqual(code, 1)
        self.assertIn("--user", err)
        code, _, _ = self.run_cli(
            "add-task", "--project", "Shared", "--title", "T", "--user", "Sam"
        )
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
