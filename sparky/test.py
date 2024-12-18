from typing import List, Optional
import typer

app = typer.Typer()


@app.command()
def test(tests: List[str], suites: List[str] = [],
         loop: Optional[int] = None, dryrun: Optional[bool] = False,
         skip_preflight: Optional[bool] = False, skip_cleanup: Optional[bool] = False):
    pass
