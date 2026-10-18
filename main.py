"""Project Tracker CLI: manage users, projects and tasks from the terminal."""
import argparse
import logging
import sys

from models import Project, Task, User, STATUSES
from utils import display
from utils.storage import DEFAULT_PATH, StorageError, load_users, save_users


class CLIError(Exception):
    """A user-facing error (bad name, duplicate, etc.)."""


# ---------- lookup helpers ----------

def get_user(users, name):
    """Return the named user or raise CLIError."""
    user = User.find_by_name(users, name)
    if user is None:
        raise CLIError(f"User '{name}' not found.")
    return user


def get_project(users, title, user_name=None):
    """Find a project by title, optionally limited to one user.

    If several users have a project with the same title, ask for --user.
    """
    candidates = users if user_name is None else [get_user(users, user_name)]
    found = [u.find_project(title) for u in candidates]
    found = [p for p in found if p is not None]
    if not found:
        raise CLIError(f"Project '{title}' not found.")
    if len(found) > 1:
        raise CLIError(
            f"More than one project is called '{title}'. Add --user to choose."
        )
    return found[0]


def get_task(project, title):
    """Return the task in a project or raise CLIError."""
    task = project.find_task(title)
    if task is None:
        raise CLIError(f"Task '{title}' not found in project '{project.title}'.")
    return task


# ---------- command handlers (each returns True if data changed) ----------

def cmd_add_user(args, users):
    if User.find_by_name(users, args.name):
        raise CLIError(f"User '{args.name}' already exists.")
    user = User(args.name, args.email or "")
    users.append(user)
    display.success(f"Added user {user.name}.")
    return True


def cmd_list_users(args, users):
    rows = [(u.id, u.name, u.email or "-", len(u.projects)) for u in users]
    display.show_table("Users", ["ID", "Name", "Email", "Projects"], rows)
    return False


def cmd_add_project(args, users):
    user = get_user(users, args.user)
    project = Project(args.title, args.description or "", args.due_date or "")
    user.add_project(project)
    display.success(f"Added project '{project.title}' to {user.name}.")
    return True


def cmd_list_projects(args, users):
    owners = [get_user(users, args.user)] if args.user else users
    rows = [
        (p.id, p.title, o.name, p.due_date or "-", len(p.tasks), f"{p.progress}%")
        for o in owners
        for p in o.projects
    ]
    display.show_table(
        "Projects", ["ID", "Title", "Owner", "Due", "Tasks", "Done"], rows
    )
    return False


def cmd_search_projects(args, users):
    owners = [get_user(users, args.user)] if args.user else users
    rows = [
        (p.id, p.title, o.name, p.due_date or "-", f"{p.progress}%")
        for o in owners
        for p in o.projects
        if p.matches(args.keyword)
    ]
    display.show_table(
        f"Projects matching '{args.keyword}'",
        ["ID", "Title", "Owner", "Due", "Done"],
        rows,
    )
    return False


def cmd_add_task(args, users):
    project = get_project(users, args.project, args.user)
    if args.assigned_to:
        get_user(users, args.assigned_to)  # must be a real user
    task = Task(args.title, assigned_to=args.assigned_to or "")
    project.add_task(task)
    display.success(f"Added task '{task.title}' to '{project.title}'.")
    return True


def cmd_list_tasks(args, users):
    project = get_project(users, args.project, args.user)
    tasks = [t for t in project.tasks if not args.status or t.status == args.status]
    rows = [(t.id, t.title, t.status, t.assigned_to or "-") for t in tasks]
    display.show_table(
        f"Tasks in '{project.title}'", ["ID", "Title", "Status", "Assigned to"], rows
    )
    return False


def cmd_complete_task(args, users):
    project = get_project(users, args.project, args.user)
    task = get_task(project, args.title)
    task.complete()
    display.success(f"Marked '{task.title}' as complete.")
    return True


def cmd_update_task(args, users):
    project = get_project(users, args.project, args.user)
    task = get_task(project, args.title)
    if args.status is None and args.assigned_to is None:
        raise CLIError("Nothing to update. Use --status and/or --assigned-to.")
    if args.status is not None:
        task.status = args.status
    if args.assigned_to is not None:
        if args.assigned_to:
            get_user(users, args.assigned_to)
        task.assigned_to = args.assigned_to
    display.success(f"Updated task '{task.title}'.")
    return True


# ---------- parser ----------

def build_parser():
    """Create the argparse parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="main.py", description="Manage users, projects and tasks."
    )
    parser.add_argument(
        "--data-file", default=str(DEFAULT_PATH), help="path to the JSON data file"
    )
    parser.add_argument("--verbose", action="store_true", help="show debug logging")
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    def add(name, handler, help_text):
        p = sub.add_parser(name, help=help_text, description=help_text)
        p.set_defaults(handler=handler)
        return p

    p = add("add-user", cmd_add_user, "Create a user")
    p.add_argument("--name", required=True)
    p.add_argument("--email")

    add("list-users", cmd_list_users, "List all users")

    p = add("add-project", cmd_add_project, "Add a project to a user")
    p.add_argument("--user", required=True, help="owner's name")
    p.add_argument("--title", required=True)
    p.add_argument("--description")
    p.add_argument("--due-date", help="YYYY-MM-DD")

    p = add("list-projects", cmd_list_projects, "List projects (optionally one user's)")
    p.add_argument("--user")

    p = add("search-projects", cmd_search_projects, "Search projects by keyword")
    p.add_argument("--keyword", required=True)
    p.add_argument("--user")

    p = add("add-task", cmd_add_task, "Add a task to a project")
    p.add_argument("--project", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--assigned-to", help="name of an existing user")
    p.add_argument("--user", help="project owner (if titles clash)")

    p = add("list-tasks", cmd_list_tasks, "List tasks in a project")
    p.add_argument("--project", required=True)
    p.add_argument("--status", choices=STATUSES)
    p.add_argument("--user", help="project owner (if titles clash)")

    p = add("complete-task", cmd_complete_task, "Mark a task complete")
    p.add_argument("--project", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--user", help="project owner (if titles clash)")

    p = add("update-task", cmd_update_task, "Change a task's status or assignee")
    p.add_argument("--project", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--status", choices=STATUSES)
    p.add_argument("--assigned-to")
    p.add_argument("--user", help="project owner (if titles clash)")

    return parser


def main(argv=None):
    """Entry point. Returns a process exit code (0 = success)."""
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )
    try:
        users = load_users(args.data_file)
        if args.handler(args, users):
            save_users(users, args.data_file)
    except (CLIError, StorageError, ValueError) as err:
        display.error(str(err))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
