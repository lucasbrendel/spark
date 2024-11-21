from typing import List, Optional
import typer
from rich import print
import task
import packet
import config
import os
from typer_shell import make_typer_shell

shell = make_typer_shell()

app = typer.Typer()
app.add_typer(task.app, name="task")
app.add_typer(packet.app, name="packet")
app.add_typer(config.app, name="config")
app.add_typer(shell, name="shell")


@app.command()
def about():
    print("Spark")


@app.command(help="Create a new Spark project environment")
def init(path: str):
    print("[green]Creating new project[/green]")
    os.makedirs(path, exist_ok=True)
    cwd = os.getcwd()
    os.chdir(path)
    # TODO Create a new config file
    os.makedirs("reports", exist_ok=True)
    os.chdir(cwd)


@app.command()
def test(tests: List[str], suites: List[str] = [],
         loop: Optional[int] = None, dryrun: Optional[bool] = False):
    pass


if __name__ == "__main__":
    app()
