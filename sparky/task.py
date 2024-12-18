import typer

app = typer.Typer()


class ITask():
    pass


@app.command()
def list():
    pass


@app.command()
def run():
    pass
