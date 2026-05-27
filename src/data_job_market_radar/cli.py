from rich.console import Console
from .config import get_settings
from .auth import get_access_token

console = Console()


def main() -> None:
    settings = get_settings()
    console.print(settings)

    token = get_access_token(settings=settings)
    console.print("[green]Token retrieved successfully[/green]")
    console.print(f"Token type: {token.token_type}")
    console.print(f"Expires in: {token.expires_in}")
    console.print(f"Expires at: {token.expires_at}")
