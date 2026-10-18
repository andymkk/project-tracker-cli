"""Project model: belongs to one user and holds many tasks."""
from models.task import Task
from utils.validators import parse_date


class Project:
    """A project with a title, description, optional due date and tasks."""

    _next_id = 1

    def __init__(self, title, description="", due_date="", project_id=None):
        self.title = title
        self.description = description or ""
        self.due_date = due_date
        self.tasks = []
        self.owner = None  # set by User.add_project
        if project_id is None:
            self.id = Project._next_id
            Project._next_id += 1
        else:
            self.id = project_id
            Project._next_id = max(Project._next_id, project_id + 1)

    @property
    def title(self):
        """The project title (never empty)."""
        return self._title

    @title.setter
    def title(self, value):
        value = (value or "").strip()
        if not value:
            raise ValueError("Project title cannot be empty.")
        self._title = value

    @property
    def due_date(self):
        """ISO date string (YYYY-MM-DD) or an empty string."""
        return self._due_date

    @due_date.setter
    def due_date(self, value):
        self._due_date = parse_date(value) if value else ""

    @property
    def progress(self):
        """Percentage of tasks complete (0 when there are no tasks)."""
        if not self.tasks:
            return 0
        done = sum(1 for t in self.tasks if t.is_complete)
        return round(100 * done / len(self.tasks))

    def add_task(self, task):
        """Attach a task, rejecting duplicate titles (case-insensitive)."""
        if self.find_task(task.title):
            raise ValueError(
                f"Task '{task.title}' already exists in project '{self.title}'."
            )
        self.tasks.append(task)
        return task

    def find_task(self, title):
        """Return the task with this title, or None."""
        wanted = title.strip().lower()
        for task in self.tasks:
            if task.title.lower() == wanted:
                return task
        return None

    def matches(self, keyword):
        """True if the keyword appears in the title or description."""
        keyword = keyword.lower()
        return keyword in self.title.lower() or keyword in self.description.lower()

    def to_dict(self):
        """Return a JSON-serialisable representation (tasks nested)."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @classmethod
    def from_dict(cls, data):
        """Rebuild a Project (and its tasks) from ``to_dict`` output."""
        project = cls(
            title=data["title"],
            description=data.get("description", ""),
            due_date=data.get("due_date", ""),
            project_id=data.get("id"),
        )
        for task_data in data.get("tasks", []):
            project.tasks.append(Task.from_dict(task_data))
        return project

    @classmethod
    def reset_counter(cls):
        """Reset the id counter (used by tests)."""
        cls._next_id = 1

    def __str__(self):
        due = f" (due {self.due_date})" if self.due_date else ""
        return f"{self.title}{due}"

    def __repr__(self):
        return f"Project(id={self.id}, title={self.title!r}, tasks={len(self.tasks)})"
