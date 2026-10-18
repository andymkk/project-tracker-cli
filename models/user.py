"""User model: a Person who owns many projects."""
from models.person import Person
from models.project import Project


class User(Person):
    """A team member. One user has many projects (one-to-many)."""

    _next_id = 1

    def __init__(self, name, email="", user_id=None):
        super().__init__(name, email)
        self.projects = []
        if user_id is None:
            self.id = User._next_id
            User._next_id += 1
        else:
            self.id = user_id
            User._next_id = max(User._next_id, user_id + 1)

    def add_project(self, project):
        """Attach a project, rejecting duplicate titles for this user."""
        if self.find_project(project.title):
            raise ValueError(
                f"{self.name} already has a project called '{project.title}'."
            )
        project.owner = self
        self.projects.append(project)
        return project

    def find_project(self, title):
        """Return this user's project with the given title, or None."""
        wanted = title.strip().lower()
        for project in self.projects:
            if project.title.lower() == wanted:
                return project
        return None

    def to_dict(self):
        """Return a JSON-serialisable representation (projects nested)."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "projects": [p.to_dict() for p in self.projects],
        }

    @classmethod
    def from_dict(cls, data):
        """Rebuild a User (with projects and tasks) from ``to_dict`` output."""
        user = cls(
            name=data["name"],
            email=data.get("email", ""),
            user_id=data.get("id"),
        )
        for project_data in data.get("projects", []):
            project = Project.from_dict(project_data)
            project.owner = user
            user.projects.append(project)
        return user

    @classmethod
    def find_by_name(cls, users, name):
        """Return the user with this name from a collection, or None."""
        wanted = name.strip().lower()
        for user in users:
            if user.name.lower() == wanted:
                return user
        return None

    @classmethod
    def reset_counter(cls):
        """Reset the id counter (used by tests)."""
        cls._next_id = 1

    def __repr__(self):
        return f"User(id={self.id}, name={self.name!r}, projects={len(self.projects)})"
