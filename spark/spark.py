from typing import List, Union
import typer
from rich import print
import task
import packet
import config
import os

app = typer.Typer()
app.add_typer(task.app, name="task")
app.add_typer(packet.app, name="packet")
app.add_typer(config.app, name="config")


@app.command()
def about():
    print("Spark")


@app.command(help="Create a new Spark project environment")
def init(path: str):
    reports = os.path.join(path, "reports")
    if not os.path.exists(reports):
        os.mkdir(reports)


@app.command()
def test(tests: List[str], suites: List[str] = [],
         loop: Union[int, None] = None, dryrun: bool = False):
    pass


if __name__ == "__main__":
    app()
