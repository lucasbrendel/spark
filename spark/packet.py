import typer

app = typer.Typer()


@app.command()
def install(packet, version: str):
    pass


@app.command()
def remove(packet):
    pass


@app.command()
def verify(packet, version: str):
    pass

@app.command()
def list():
    pass
