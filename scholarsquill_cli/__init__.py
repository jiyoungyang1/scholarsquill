#!/usr/bin/env python3
"""
ScholarsQuill CLI - Installation and management tool for ScholarsQuill
Academic PDF processing with MCP server integration

Usage:
    scholarsquill install        # Install slash commands to Claude Code
    scholarsquill uninstall      # Remove slash commands
    scholarsquill check          # Check installation status
    scholarsquill version        # Show version
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

app = typer.Typer(
    name="scholarsquill",
    help="Installation and management tool for ScholarsQuill academic PDF processing",
    add_completion=False,
)

# Version
VERSION = "0.1.0"

# Paths
CLAUDE_CONFIG_DIR = Path.home() / "Library/Application Support/Claude"
CLAUDE_COMMANDS_DIR = Path.home() / ".claude" / "commands"
CLAUDE_CONFIG_FILE = CLAUDE_CONFIG_DIR / "claude_desktop_config.json"

def get_package_root() -> Path:
    """Get the ScholarsQuill package root directory."""
    return Path(__file__).parent.parent


@app.command()
def install(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing command files"),
):
    """
    Install ScholarsQuill slash commands to Claude Code.

    This will:
    1. Create ~/.claude/commands/ directory if needed
    2. Copy note.md, citemap.md, codelang.md to ~/.claude/commands/
    3. Configure MCP server in Claude Desktop config (if not already configured)
    4. Provide restart instructions
    """
    console.print(Panel("[cyan]ScholarsQuill Installation[/cyan]", border_style="cyan"))

    # Check if commands directory exists
    if not CLAUDE_COMMANDS_DIR.exists():
        console.print(f"Creating commands directory: {CLAUDE_COMMANDS_DIR}")
        CLAUDE_COMMANDS_DIR.mkdir(parents=True, exist_ok=True)

    # Get source command files from package
    package_root = get_package_root()
    source_commands_dir = package_root / ".claude" / "commands"

    if not source_commands_dir.exists():
        console.print(f"[red]Error:[/red] Command files not found in package at {source_commands_dir}")
        raise typer.Exit(1)

    # Copy command files
    commands = ["note.md", "citemap.md", "codelang.md"]
    installed = []
    skipped = []

    for cmd_file in commands:
        source = source_commands_dir / cmd_file
        dest = CLAUDE_COMMANDS_DIR / cmd_file

        if not source.exists():
            console.print(f"[yellow]Warning:[/yellow] {cmd_file} not found in package")
            continue

        if dest.exists() and not force:
            skipped.append(cmd_file)
            continue

        shutil.copy2(source, dest)
        installed.append(cmd_file)
        console.print(f"[green]✓[/green] Installed: {cmd_file}")

    # Check MCP server configuration
    console.print("\n[cyan]Checking MCP server configuration...[/cyan]")

    if not CLAUDE_CONFIG_FILE.exists():
        console.print(f"[yellow]Warning:[/yellow] Claude config not found at {CLAUDE_CONFIG_FILE}")
        console.print("You'll need to manually configure the MCP server.")
    else:
        with open(CLAUDE_CONFIG_FILE, 'r') as f:
            config = json.load(f)

        if "mcpServers" not in config:
            config["mcpServers"] = {}

        if "scholarsquill" not in config["mcpServers"]:
            console.print("[yellow]MCP server not configured.[/yellow] Add this to your Claude config:")

            example_config = {
                "scholarsquill": {
                    "command": "/usr/local/bin/python3",
                    "args": ["-m", "src.legacy_mcp_server.server"],
                    "cwd": str(package_root),
                    "env": {
                        "PYTHONPATH": str(package_root)
                    }
                }
            }

            console.print(Panel(
                json.dumps(example_config, indent=2),
                title="MCP Server Configuration",
                border_style="yellow"
            ))
        else:
            console.print("[green]✓[/green] MCP server already configured")

    # Summary
    console.print("\n[bold green]Installation Summary[/bold green]")
    table = Table(show_header=False, border_style="cyan")
    table.add_row("Installed commands:", ", ".join(installed) if installed else "None")
    if skipped:
        table.add_row("[yellow]Skipped (use --force):[/yellow]", ", ".join(skipped))
    console.print(table)

    # Next steps
    console.print("\n[bold cyan]Next Steps:[/bold cyan]")
    console.print("1. Restart Claude Code completely")
    console.print("2. Commands will be available: /note, /citemap, /codelang")
    console.print("3. Test with: /note --help")


@app.command()
def uninstall():
    """Remove ScholarsQuill slash commands from Claude Code."""
    console.print(Panel("[yellow]ScholarsQuill Uninstallation[/yellow]", border_style="yellow"))

    commands = ["note.md", "citemap.md", "codelang.md"]
    removed = []

    for cmd_file in commands:
        dest = CLAUDE_COMMANDS_DIR / cmd_file
        if dest.exists():
            dest.unlink()
            removed.append(cmd_file)
            console.print(f"[green]✓[/green] Removed: {cmd_file}")

    if removed:
        console.print(f"\n[green]Removed {len(removed)} command(s)[/green]")
        console.print("[yellow]Note:[/yellow] MCP server configuration in Claude config was not changed")
        console.print("Restart Claude Code to complete uninstallation")
    else:
        console.print("[yellow]No ScholarsQuill commands found to remove[/yellow]")


@app.command()
def check():
    """Check ScholarsQuill installation status."""
    console.print(Panel("[cyan]ScholarsQuill Installation Status[/cyan]", border_style="cyan"))

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Location", style="dim")

    # Check commands directory
    if CLAUDE_COMMANDS_DIR.exists():
        table.add_row("Commands directory", "[green]✓ Found[/green]", str(CLAUDE_COMMANDS_DIR))
    else:
        table.add_row("Commands directory", "[red]✗ Missing[/red]", str(CLAUDE_COMMANDS_DIR))

    # Check individual commands
    commands = ["note.md", "citemap.md", "codelang.md"]
    for cmd_file in commands:
        dest = CLAUDE_COMMANDS_DIR / cmd_file
        if dest.exists():
            table.add_row(f"/{cmd_file.replace('.md', '')}", "[green]✓ Installed[/green]", str(dest))
        else:
            table.add_row(f"/{cmd_file.replace('.md', '')}", "[red]✗ Missing[/red]", str(dest))

    # Check MCP config
    if CLAUDE_CONFIG_FILE.exists():
        with open(CLAUDE_CONFIG_FILE, 'r') as f:
            config = json.load(f)

        if "mcpServers" in config and "scholarsquill" in config["mcpServers"]:
            table.add_row("MCP server config", "[green]✓ Configured[/green]", str(CLAUDE_CONFIG_FILE))
        else:
            table.add_row("MCP server config", "[yellow]⚠ Not configured[/yellow]", str(CLAUDE_CONFIG_FILE))
    else:
        table.add_row("MCP server config", "[red]✗ File missing[/red]", str(CLAUDE_CONFIG_FILE))

    console.print(table)

    # Check Python dependencies
    console.print("\n[cyan]Python Dependencies:[/cyan]")
    deps_table = Table(show_header=True, header_style="bold cyan")
    deps_table.add_column("Package", style="cyan")
    deps_table.add_column("Status", style="white")

    required_packages = ["mcp", "PyPDF2", "pdfplumber", "jinja2", "networkx"]
    for pkg in required_packages:
        try:
            __import__(pkg)
            deps_table.add_row(pkg, "[green]✓ Installed[/green]")
        except ImportError:
            deps_table.add_row(pkg, "[red]✗ Missing[/red]")

    console.print(deps_table)


@app.command()
def version():
    """Show ScholarsQuill version."""
    console.print(f"[cyan]ScholarsQuill[/cyan] version [bold]{VERSION}[/bold]")


def main():
    """Main entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
