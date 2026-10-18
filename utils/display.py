"""Terminal output. Uses ``rich`` for tables when available."""
import sys

try:
    from rich.console import Console
    from rich.markup import escape
    from rich.table import Table

    HAS_RICH = True
except ImportError:  # plain-text fallback keeps the tool usable
    HAS_RICH = False


def _plain_table(title, columns, rows):
    print(title)
    widths = [
        max(len(str(col)), *(len(str(r[i])) for r in rows))
        for i, col in enumerate(columns)
    ]
    print("  ".join(str(c).ljust(w) for c, w in zip(columns, widths)))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print("  ".join(str(c).ljust(w) for c, w in zip(row, widths)))


def show_table(title, columns, rows):
    """Print a table; rows is a list of tuples matching columns."""
    if not rows:
        message("Nothing to show.")
        return
    if HAS_RICH:
        table = Table(title=title)
        for col in columns:
            table.add_column(col)
        for row in rows:
            table.add_row(*(escape(str(cell)) for cell in row))
        Console().print(table)
    else:
        _plain_table(title, columns, rows)


def message(text):
    """Print an informational message."""
    if HAS_RICH:
        Console().print(escape(text))
    else:
        print(text)


def success(text):
    """Print a success message."""
    if HAS_RICH:
        Console().print(f"[green]{escape(text)}[/green]")
    else:
        print(text)


def error(text):
    """Print an error message to stderr."""
    if HAS_RICH:
        Console(file=sys.stderr).print(f"[red]Error:[/red] {escape(text)}")
    else:
        print(f"Error: {text}", file=sys.stderr)
