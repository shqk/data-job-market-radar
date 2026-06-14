import typer
from rich.console import Console
from data_job_market_radar.config import get_settings
from data_job_market_radar.auth import get_access_token, AuthenticationError
from data_job_market_radar.france_travail_client import (
    FranceTravailClient,
    FranceTravailApiError,
)
from data_job_market_radar.storage import save_raw_search_response
from pathlib import Path

app = typer.Typer()
console = Console()


@app.command()
def api_smoke_test() -> None:
    try:
        settings = get_settings()
        # console.print(settings)

        token = get_access_token(settings=settings)
        console.print("[green]Token retrieved successfully[/green]")
        console.print(f"Token type: {token.token_type}")
        console.print(f"Expires in: {token.expires_in}")
        console.print(f"Expires at: {token.expires_at}")

        client = FranceTravailClient(settings=settings, token=token)

        response = client.search_jobs("data engineer", "0-1")

        console.print("[green]Search request succeeded[/green]")
        payload = response.json()
        console.print(f"Number of results: {len(payload.get('resultats', []))}")
    except AuthenticationError as exc:
        console.print(f"[red]Authentication failed:[/red] {exc}")
        raise SystemExit(1) from exc
    except FranceTravailApiError as exc:
        console.print(f"[red]France Travail API request failed:[/red] {exc}")
        raise SystemExit(1) from exc


@app.command()
def ingest_raw_sample() -> None:
    try:
        settings = get_settings()
        token = get_access_token(settings=settings)

        client = FranceTravailClient(settings=settings, token=token)
        query = "data engineer"
        range_ = "0-100"

        response = client.search_jobs("data engineer", "0-100")

        save_raw_search_response(
            Path("data/raw"), query=query, range_=range_, response=response
        )

    except AuthenticationError as exc:
        console.print(f"[red]Authentication failed:[/red] {exc}")
        raise SystemExit(1) from exc
    except FranceTravailApiError as exc:
        console.print(f"[red]France Travail API request failed:[/red] {exc}")
        raise SystemExit(1) from exc


def main() -> None:
    app()


if __name__ == "__main__":
    main()
