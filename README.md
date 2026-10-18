# Project Tracker CLI
Andy Kimathi

A command-line tool for managing **users**, their **projects** and each project's **tasks**. Data is saved to a local JSON file.
 Features
- Create and list users (name, optional email)
- Add projects to users, list them, and search by keyword
- Add tasks to projects, assign them to users, update status, mark complete
- Data persists in data/data.json between runs
- Clear error messages 


Setup
Requires Python 3.10+.


 Project structure
main.py            CLI entry point 
models/            Person -> User -> Project -> Task classes
utils/             storage (JSON), display (rich), validators
data/data.json     saved data
tests/             unit and CLI tests


 Design
- **Relationships:** User has many Projects; Project has many Tasks (one-to-many each).
- **OOP features:** `User` inherits from `Person`; `@property` setters validate names, emails, dates and statuses; class attributes provide id counters; `to_dict` / `from_dict` class methods handle JSON; `__str__` / `__repr__` give readable output.
- **Persistence:** nested JSON, written atomically; a missing file means an empty database and a corrupt file gives a friendly error.

Testing-pytest

 Known issues
- Names and titles are matched case-insensitively; renaming users or projects is not supported yet.
- There is no delete command yet.
- Tasks have a single assignee.
