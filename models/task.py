"""Task model: the smallest unit of work in a project."""

STATUSES = ("pending", "in-progress", "complete")


class Task:
    """A single task that belongs to a project.

    Class attribute ``_next_id`` hands out unique ids.
    """

    _next_id = 1

    def __init__(self, title, status="pending", assigned_to="", task_id=None):
        self.title = title
        self.status = status
        self.assigned_to = assigned_to
        if task_id is None:
            self.id = Task._next_id
            Task._next_id += 1
        else:
            self.id = task_id
            Task._next_id = max(Task._next_id, task_id + 1)

    @property
    def title(self):
        """The task title (never empty)."""
        return self._title

    @title.setter
    def title(self, value):
        value = (value or "").strip()
        if not value:
            raise ValueError("Task title cannot be empty.")
        self._title = value

    @property
    def status(self):
        """One of 'pending', 'in-progress' or 'complete'."""
        return self._status

    @status.setter
    def status(self, value):
        if value not in STATUSES:
            raise ValueError(
                f"Invalid status '{value}'. Choose from: {', '.join(STATUSES)}."
            )
        self._status = value

    @property
    def is_complete(self):
        """True when the task has been finished."""
        return self._status == "complete"

    def complete(self):
        """Mark the task as complete."""
        self.status = "complete"

    def to_dict(self):
        """Return a JSON-serialisable representation."""
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "assigned_to": self.assigned_to,
        }

    @classmethod
    def from_dict(cls, data):
        """Rebuild a Task from ``to_dict`` output."""
        return cls(
            title=data["title"],
            status=data.get("status", "pending"),
            assigned_to=data.get("assigned_to", ""),
            task_id=data.get("id"),
        )

    @classmethod
    def reset_counter(cls):
        """Reset the id counter (used by tests)."""
        cls._next_id = 1

    def __str__(self):
        return f"[{self.status}] {self.title}"

    def __repr__(self):
        return f"Task(id={self.id}, title={self.title!r}, status={self.status!r})"
