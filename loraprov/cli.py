"""
loraprov.cli
~~~~~~~~~~~~

Command‑line entry point powered by Typer.

Usage examples
--------------
Generate a key:

    loraprov key generate alice

Sign an adapter:

    loraprov sign adapter.safetensors --parent-sha 6efa... --license MIT --key alice

Verify:

    loraprov verify adapter.safetensors
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .core import sign, verify
from .keycli import KeyManager

app = typer.Typer(add_completion=False, help="LoRA / adapter provenance toolkit")
console = Console()

km = KeyManager()  # singleton for this process


# ---------- key sub‑commands ---------- #
key_app = typer.Typer(help="Manage Ed25519 keys")
app.add_typer(key_app, name="key")


@key_app.command("generate")
def key_generate(name: str, overwrite: bool = typer.Option(False, "--overwrite")):
    """Create a new key."""
    pub_hex = km.generate(name, overwrite=overwrite)
    console.print(f"[green]✔[/] Key [cyan]{name}[/] created. Public key:\n{pub_hex}")


@key_app.command("list")
def key_list():
    """Show all stored keys."""
    data = km.list()
    if not data:
        console.print("No keys found. Run [bold]loraprov key generate[/] first.")
        raise typer.Exit(code=1)

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name")
    table.add_column("Public key")
    for k, v in data.items():
        table.add_row(k, v)
    console.print(table)


# ---------- sign ---------- #
@app.command("sign")
def sign_cmd(
    adapter: Path = typer.Argument(..., exists=True, readable=True),
    parent_sha: str = typer.Option(..., "--parent-sha", help="SHA‑256 of base model"),
    license: str = typer.Option(..., "--license"),
    key: str = typer.Option("default", "--key", help="Key name to sign with"),
):
    """Create `<adapter>.sig`."""
    sig_file = sign(adapter, parent_sha=parent_sha, license=license, key_name=key)
    console.print(f"[green]✔[/] Signature written to [cyan]{sig_file}[/]")


# ---------- verify ---------- #
@app.command("verify")
def verify_cmd(
    adapter: Path = typer.Argument(..., exists=True, readable=True),
    policy: str = typer.Option("default", "--policy"),
):
    """Verify `<adapter>.sig`."""
    ok, msg = verify(adapter, policy=policy)
    if ok:
        console.print(f"[green]✔[/] {msg}")
        raise typer.Exit(code=0)
    else:
        console.print(f"[red]✖[/] {msg}")
        raise typer.Exit(code=1)


@app.command("sbom")
def sbom_cmd(
    adapter: Path = typer.Argument(..., exists=True, readable=True),
    out: Path = typer.Option("sbom.json", "--out"),
):
    """Export CycloneDX SBOM for adapter."""
    from .sbom import export_cyclonedx

    export_cyclonedx(adapter, out)
    console.print(f"[green]✔[/] SBOM written to [cyan]{out}[/]")


# ---------- main ---------- #
def _main():
    app()


if __name__ == "__main__":  # pragma: no cover
    _main()
