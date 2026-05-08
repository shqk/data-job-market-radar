from rich.console import Console
from config import get_settings

console = Console()

settings = get_settings()

console.print(settings)