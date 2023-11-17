import logging
from pathlib import Path
from typing import Annotated

import typer
from rich.logging import RichHandler

HERE = Path(__file__).parent

app = typer.Typer(no_args_is_help=True)


@app.command()
def api(
    *,
    reload: Annotated[bool, typer.Option(envvar="DEBUG")] = False,
) -> None:
    """Start the API server."""
    import uvicorn

    uvicorn.run(
        "fastapi_sqlalchemy_crud.server:app",
        host="127.0.0.1",
        port=8000,
        reload=reload,
        use_colors=True,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, handlers=[RichHandler()])
    app()
