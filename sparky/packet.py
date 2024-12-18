import typer

app = typer.Typer()

class IPacket():

    def install(self, version:str):
        pass

    def remove(self):
        pass

    def verify(self, version:str):
        pass


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
