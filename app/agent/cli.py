"""Command‑line interface for the ResearchAgent.

The CLI uses **Typer** to expose a single ``ask`` command that forwards the
provided query to the LLM via :class:`~app.agent.research_agent.ResearchAgent`
and prints the answer to stdout.

Running the module directly works:

    python -m app.agent.cli ask "What is recursion?"

Optional flags allow you to override the model identifier and provider without
touching environment variables.
"""

from __future__ import annotations

import typer

from .research_agent import ResearchAgent

app = typer.Typer(add_completion=False, help="Simple Research Agent CLI")


@app.command()
def ask(
    query: str = typer.Argument(..., help="The question or research query to send to the LLM"),
    model: str = typer.Option("gpt-oss:120b-cloud", "--model", help="Model identifier to use"),
    provider: str | None = typer.Option(None, "--provider", help="LLM provider name (overrides LLM_PROVIDER env var)"),
) -> None:
    """Send *query* to the LLM and print the answer.

    The command simply constructs a :class:`ResearchAgent` with the provided
    configuration and calls its :meth:`ResearchAgent.ask` method.
    """
    agent = ResearchAgent(model=model, provider=provider)
    answer = agent.ask(query)
    typer.echo(answer)


if __name__ == "__main__":
    # Allows ``python app/agent/cli.py`` execution during development.
    app()
