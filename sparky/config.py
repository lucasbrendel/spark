
from typing import Annotated
import typer
from typer import Argument

app = typer.Typer()


@app.command(help="Get configuration value of specified key")
def get(key: Annotated[str, Argument()]):
    pass

@app.command(help="Set a value to a key")
def set(key: Annotated[str, Argument()], value):
    pass


@app.command(help="List out all configuration key value pairs")
def list():
    pass


@app.command(help="Remove a configuration key/value pair from the configuration file.")
def remove(key: Annotated[str, Argument()]):
    pass
