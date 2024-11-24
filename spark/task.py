import typer

from spark.core import Interface

app = typer.Typer()


class ITask(Interface):
    pass


@app.command()
def list():
    pass


@app.command()
def run():
    pass
