from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def show_quest_header(title: str, subtitle: str) -> None:
    console.print(
        Panel.fit(
            f"[bold magenta]{title}[/bold magenta]\n[cyan]{subtitle}[/cyan]",
            border_style="magenta",
        )
    )


def narrator(message: str) -> None:
    console.print(f"\n[bold violet]🧙 Zhyréon:[/bold violet] {message}\n")


def success(message: str) -> None:
    console.print(f"[bold green]✅ {message}[/bold green]")


def warning(message: str) -> None:
    console.print(f"[bold yellow]⚠️ {message}[/bold yellow]")


def agent(message: str) -> None:
    console.print(f"\n[bold cyan]🤖 Agente:[/bold cyan] {message}\n")


def user_prompt() -> str:
    return console.input("[bold white]🧑 Tú > [/bold white]")

def show_prompt(message: str) -> None:
    console.print(f"[bold white]🧑 Prompt:[/bold white] {message}\n")