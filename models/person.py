"""Base class shared by anything that represents a person."""
import re

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Person:
    """A named person with an optional, validated email address.

    ``name`` and ``email`` are exposed as properties so every assignment
    goes through validation (encapsulation).
    """

    def __init__(self, name, email=""):
        self.name = name
        self.email = email

    @property
    def name(self):
        """The person's display name."""
        return self._name

    @name.setter
    def name(self, value):
        value = (value or "").strip()
        if not value:
            raise ValueError("Name cannot be empty.")
        self._name = value

    @property
    def email(self):
        """The person's email address (may be an empty string)."""
        return self._email

    @email.setter
    def email(self, value):
        value = (value or "").strip()
        if value and not _EMAIL_PATTERN.match(value):
            raise ValueError(f"'{value}' is not a valid email address.")
        self._email = value

    def __str__(self):
        return self.name if not self.email else f"{self.name} <{self.email}>"
