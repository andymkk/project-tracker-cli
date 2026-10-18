# Project Tracker CLI
Andy Kimathi

A command-line tool for managing **users**, their **projects** and each project's **tasks**. Data is saved to a local JSON file.

## Features
- Create and list users (name, optional email)
- Add projects to users, list them, and search by keyword
- Add tasks to projects, assign them to users, update status, mark complete
- Data persists in `data/data.json` between runs
- Clear error messages (unknown user, duplicate names, bad dates, corrupt data file)
- Pretty tables with [`rich`](https://pypi.org/project/rich/) (falls back to plain text if it is not installed)

## Setup
Requires Python 3.10+.

```bash
git clone <your-repo-url>
cd project-tracker-cli
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage
```bash
python main.py add-user --name "Alex" --email alex@example.com
python main.py add-project --user "Alex" --title "CLI Tool" --description "Build it" --due-date 2026-11-30
python main.py add-task --project "CLI Tool" --title "Implement add-task" --assigned-to "Alex"
python main.py complete-task --project "CLI Tool" --title "Implement add-task"
python main.py list-projects --user "Alex"
python main.py search-projects --keyword cli
```

| Command | Purpose | Options |
|---|---|---|
| `add-user` | Create a user | `--name` (required), `--email` |
| `list-users` | List all users | |
| `add-project` | Add a project to a user | `--user`, `--title` (required), `--description`, `--due-date YYYY-MM-DD` |
| `list-projects` | List projects | `--user` |
| `search-projects` | Search title/description | `--keyword` (required), `--user` |
| `add-task` | Add a task to a project | `--project`, `--title` (required), `--assigned-to`, `--user` |
| `list-tasks` | List a project's tasks | `--project` (required), `--status`, `--user` |
| `complete-task` | Mark a task complete | `--project`, `--title` (required), `--user` |
| `update-task` | Change status or assignee | `--project`, `--title` (required), `--status`, `--assigned-to`, `--user` |

Global options (put before the command): `--data-file PATH` to use a different JSON file, `--verbose` for debug logging. Use `python main.py COMMAND --help` for help on any command.

If two users have a project with the same title, add `--user "<owner>"` so the tool knows which one you mean.

## Project structure
```
main.py            CLI entry point (argparse subcommands)
models/            Person -> User -> Project -> Task classes
utils/             storage (JSON), display (rich), validators
data/data.json     saved data
tests/             unit and CLI tests
```

### Design
- **Relationships:** User has many Projects; Project has many Tasks (one-to-many each).
- **OOP features:** `User` inherits from `Person`; `@property` setters validate names, emails, dates and statuses; class attributes provide id counters; `to_dict` / `from_dict` class methods handle JSON; `__str__` / `__repr__` give readable output.
- **Persistence:** nested JSON, written atomically; a missing file means an empty database and a corrupt file gives a friendly error.

## Testing
```bash
pytest
```
(`python -m unittest discover -s tests -t .` also works.)

## Known issues
- Names and titles are matched case-insensitively; renaming users or projects is not supported yet.
- There is no delete command yet.
- Tasks have a single assignee.
