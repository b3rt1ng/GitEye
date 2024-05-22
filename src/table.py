from rich.console import Console
from rich.table import Table

colors = [
    "bright_red",
    "bright_green",
    "bright_yellow",
    "bright_blue",
    "bright_magenta",
    "bright_cyan",
    "bright_white"
]

console = Console()

def show_table(data: list, column_names: list, title: str = "", redundancy: bool = False):
    """
    Show a table with the given data
        :param data: The data to show
        :param column_names: The names of the columns
        :param title: The title of the table
        :param redundancy: If False, a data already shown will not be shown again
    """
    table = Table(title=title)
    for column_name, color in zip(column_names, colors):
        table.add_column(column_name, style=color)

    if redundancy:
        for row in data:
            table.add_row(*row)
    else:
        for row in set(zip(*data)):
            table.add_row(*row)

    console.print(table)