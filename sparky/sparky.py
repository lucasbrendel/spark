from typing import List, Optional

import config
import packet
import task
import typer
from rich import print
import rich.traceback
from typer_shell import make_typer_shell

import test

# Make Rich be the stack trace handler
rich.traceback.install(show_locals=True)

shell = make_typer_shell(prompt=">>")

app = typer.Typer()
app.add_typer(task.app, name="task")
app.add_typer(packet.app, name="packet")
app.add_typer(shell, name="shell")
app.add_typer(test.app, name="test")
app.add_typer(config.app, name="config")



@app.command()
@shell.command()
def about():
    print("Sparky")


@app.command(help="Create a new Sparky project environment")
def init(path: str):
    print("[green]Creating new project[/green]")


@app.command(help="Restart the environment")
def reload():
    pass


@app.command()
def clear():
    pass

@app.command()
def upgrade():
    pass


if __name__ == "__main__":
    app()
