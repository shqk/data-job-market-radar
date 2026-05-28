from rich.console import Console
from .config import get_settings
from .auth import get_access_token
from .france_travail_client import FranceTravailClient

console = Console()


def main() -> None:
    settings = get_settings()
    console.print(settings)

    token = get_access_token(settings=settings)
    console.print("[green]Token retrieved successfully[/green]")
    console.print(f"Token type: {token.token_type}")
    console.print(f"Expires in: {token.expires_in}")
    console.print(f"Expires at: {token.expires_at}")

    client = FranceTravailClient(settings=settings, token=token)

    response = client.search_jobs("data engineer", "0-1")

    console.print("[green]Search request succeeded[/green]")
    console.print(f"Status code: {response.status_code}")
    console.print(f"Content-Range: {response.headers.get('content-range')}")
    console.print(f"Accept-Range: {response.headers.get('accept-range')}")

    payload = response.json()
    console.print(f"Number of results: {len(payload.get('resultats', []))}")

