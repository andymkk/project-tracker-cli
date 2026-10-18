"""Unit tests for the domain models."""
import unittest

from models import Person, Project, Task, User


class BaseCase(unittest.TestCase):
    def setUp(self):
        for cls in (User, Project, Task):
            cls.reset_counter()


class TestPerson(BaseCase):
    def test_name_is_stripped(self):
        self.assertEqual(Person("  Alex ").name, "Alex")

    def test_empty_name_rejected(self):
        with self.assertRaises(ValueError):
            Person("   ")

    def test_bad_email_rejected(self):
        with self.assertRaises(ValueError):
            Person("Alex", "not-an-email")

    def test_valid_email_accepted(self):
        self.assertEqual(Person("Alex", "a@b.co").email, "a@b.co")


class TestTask(BaseCase):
    def test_default_status_is_pending(self):
        self.assertEqual(Task("Write docs").status, "pending")

    def test_complete(self):
        task = Task("Write docs")
        task.complete()
        self.assertTrue(task.is_complete)

    def test_invalid_status_rejected(self):
        with self.assertRaises(ValueError):
            Task("Write docs", status="done-ish")

    def test_ids_increment(self):
        self.assertEqual(Task("a").id + 1, Task("b").id)

    def test_round_trip(self):
        task = Task("Write docs", "in-progress", "Alex")
        copy = Task.from_dict(task.to_dict())
        self.assertEqual(copy.to_dict(), task.to_dict())


class TestProject(BaseCase):
    def test_progress(self):
        project = Project("P")
        self.assertEqual(project.progress, 0)
        a = project.add_task(Task("a"))
        project.add_task(Task("b"))
        a.complete()
        self.assertEqual(project.progress, 50)

    def test_duplicate_task_rejected(self):
        project = Project("P")
        project.add_task(Task("a"))
        with self.assertRaises(ValueError):
            project.add_task(Task("A"))

    def test_bad_due_date_rejected(self):
        with self.assertRaises(ValueError):
            Project("P", due_date="31/12/2026")

    def test_matches_keyword(self):
        project = Project("CLI Tool", "uses argparse")
        self.assertTrue(project.matches("argparse"))
        self.assertFalse(project.matches("django"))


class TestUser(BaseCase):
    def test_user_is_a_person(self):
        self.assertIsInstance(User("Alex"), Person)

    def test_add_project_sets_owner(self):
        user = User("Alex")
        project = user.add_project(Project("P"))
        self.assertIs(project.owner, user)

    def test_duplicate_project_rejected(self):
        user = User("Alex")
        user.add_project(Project("P"))
        with self.assertRaises(ValueError):
            user.add_project(Project("p"))

    def test_find_by_name_case_insensitive(self):
        users = [User("Alex")]
        self.assertIs(User.find_by_name(users, "alex"), users[0])
        self.assertIsNone(User.find_by_name(users, "Sam"))

    def test_nested_round_trip(self):
        user = User("Alex", "a@b.co")
        project = user.add_project(Project("P", "d", "2026-12-31"))
        project.add_task(Task("t", assigned_to="Alex"))
        copy = User.from_dict(user.to_dict())
        self.assertEqual(copy.to_dict(), user.to_dict())
        self.assertIs(copy.projects[0].owner, copy)


if __name__ == "__main__":
    unittest.main()
