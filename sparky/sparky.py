from typing import Annotated, List, Optional
import os
import sys
import config
import packet
import task
import typer
from rich import print
import rich.traceback
from typer_shell import make_typer_shell

# Make Rich be the stack trace handler
rich.traceback.install(show_locals=True)

shell = make_typer_shell(intro="Welcome to Sparky!")

app = typer.Typer()

app.add_typer(task.app, name="task")
app.add_typer(packet.app, name="packet")
app.add_typer(shell, name="shell")
app.add_typer(config.app, name="config")

shell.add_typer(task.app, name="task")
shell.add_typer(packet.app, name="packet")
shell.add_typer(config.app, name="config")


@app.command(help="Print information about Sparky")
@shell.command(help="Print information about Sparky")
def about():
    print("Sparky")


@app.command(help="Create a new Sparky project environment")
def init(path: Annotated[str, typer.Argument()]):
    print("[green]Creating new project[/green]")


@app.command(help="Upgrade Sparky environment to latest version.")
def upgrade():
    pass

@app.command(help="List registered modules")
@shell.command(help="List registered modules")
def modules():
    pass


@shell.command(help="Restart the environment")
def reload():
    os.execv(sys.executable, sys.argv)


@shell.command(help="Clear the shell screen")
def clear():
    pass


@app.command(help="Execute a series or suite of tests.")
@shell.command(help="Execute a series or suite of tests.")
def test(tests: List[str], suites: Annotated[str, typer.Option(help="Test suites to run")],
         loop: Optional[int] = None, dryrun: Optional[bool] = False,
         skip_preflight: Optional[bool] = False, skip_cleanup: Optional[bool] = False):
    pass

@app.callback()
def main(env: str = "."):
    print(f"Loading environment {os.path.realpath(env)}")

if __name__ == "__main__":
    app()
