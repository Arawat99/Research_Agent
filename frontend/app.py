"""Gradio frontend for the research-agent HTTP service."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import gradio as gr

if __package__:
    from .research import (
        follow_research,
        progress_html,
        reset_research,
        sources_html,
        start_research,
    )
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from frontend.research import (
        follow_research,
        progress_html,
        reset_research,
        sources_html,
        start_research,
    )


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

CSS = Path(__file__).with_name("styles.css").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Gradio application
# ---------------------------------------------------------------------------

with gr.Blocks(
    title="Research Agent",
) as demo:

    job_id = gr.State("")

    with gr.Row(
        elem_classes="app-shell",
        equal_height=False,
    ):

        # ---------------------------------------------------------------
        # Sidebar
        # ---------------------------------------------------------------

        with gr.Column(
            elem_classes="sidebar",
            scale=0,
            min_width=235,
        ):

            gr.HTML(
                """
                <div class="brand">
                    <div class="brand-title">
                        Research Agent
                    </div>

                    <span class="brand-subtitle">
                        AI-powered deep research
                    </span>
                </div>
                """
            )

            new_button = gr.Button(
                "＋  New Research",
                elem_classes="sidebar-button",
            )

        # ---------------------------------------------------------------
        # Main
        # ---------------------------------------------------------------

        with gr.Column(
            elem_classes="main-content",
            scale=1,
        ):

            # Header
            gr.HTML(
                """
                <div class="eyebrow">
                    Deep Research
                </div>

                <h1 class="page-title">
                    New Research
                </h1>

                <div class="page-description">
                    Ask a question and let the research agent investigate,
                    compare sources, and synthesize an answer.
                </div>
                """
            )

            # Question
            with gr.Row(
                elem_classes="question-container",
                equal_height=True,
            ):

                query = gr.Textbox(
                    show_label=False,
                    placeholder="What would you like to research?",
                    lines=1,
                    elem_classes="question-input",
                    scale=5,
                )

                start_button = gr.Button(
                    "▶  Start Research",
                    elem_classes="start-button",
                    scale=0,
                    min_width=155,
                )

            gr.HTML(
                """
                <div class="hint">
                    💡 Be specific for better results.
                </div>
                """
            )

            # Workspace
            with gr.Row(
                elem_classes="workspace",
                equal_height=False,
            ):

                # -------------------------------------------------------
                # Research column
                # -------------------------------------------------------

                with gr.Column(
                    elem_classes="research-column",
                    scale=1,
                    min_width=0,
                ):

                    # Progress
                    with gr.Column(
                        elem_classes="panel",
                    ):

                        with gr.Row(
                            elem_classes="panel-header",
                        ):

                            with gr.Column(scale=1):
                                gr.HTML(
                                    """
                                    <div class="panel-title">
                                        Research Progress
                                    </div>

                                    <div class="panel-subtitle">
                                        Live activity from the research agent
                                    </div>
                                    """
                                )

                            status = gr.Markdown(
                                "Pending",
                                elem_classes="status",
                            )

                        progress = gr.HTML(
                            progress_html({}),
                            elem_classes="progress-container",
                        )

                    # Answer
                    with gr.Column(
                        elem_classes="panel answer-panel",
                    ):

                        gr.HTML(
                            """
                            <div class="panel-title">
                                ✦ Research Answer
                            </div>

                            <div class="panel-subtitle">
                                Synthesized from the collected research
                            </div>
                            """
                        )

                        answer = gr.Markdown(
                            "Your evidence-based answer will appear here.",
                            elem_classes="answer-box",
                        )

                        gr.HTML(
                            """
                            <div class="footer-note">
                                ⓘ This report is AI-generated.
                                Verify important information before
                                making decisions.
                            </div>
                            """
                        )

                # -------------------------------------------------------
                # Right column
                # -------------------------------------------------------

                with gr.Column(
                    elem_classes="right-column",
                    scale=0,
                    min_width=270,
                ):

                    # Sources
                    with gr.Column(
                        elem_classes="panel",
                    ):

                        gr.HTML(
                            """
                            <div class="panel-title">
                                Sources
                            </div>

                            <div class="panel-subtitle">
                                Evidence collected during research
                            </div>
                            """
                        )

                        sources = gr.HTML(
                            sources_html({}),
                        )

                    # Settings
                    with gr.Column(
                        elem_classes="panel settings",
                    ):

                        gr.HTML(
                            """
                            <div class="panel-title">
                                Research Settings
                            </div>

                            <div class="panel-subtitle">
                                Configure how the agent researches
                            </div>
                            """
                        )

                        model = gr.Textbox(
                            value="openrouter/free",
                            label="Model",
                        )

                        max_rounds = gr.Slider(
                            minimum=1,
                            maximum=20,
                            value=3,
                            step=1,
                            label="Max rounds",
                        )

                        min_sources = gr.Slider(
                            minimum=1,
                            maximum=20,
                            value=2,
                            step=1,
                            label="Minimum sources",
                        )

                        num_tasks = gr.Slider(
                            minimum=1,
                            maximum=20,
                            value=3,
                            step=1,
                            label="Research tasks",
                        )

            error = gr.Markdown(
                visible=False,
                elem_classes="error-message",
            )

    # -------------------------------------------------------------------
    # Events
    # -------------------------------------------------------------------

    start_button.click(
        start_research,
        inputs=[
            query,
            model,
            max_rounds,
            min_sources,
            num_tasks,
        ],
        outputs=[
            job_id,
            status,
            progress,
            answer,
            sources,
            error,
        ],
    ).then(
        follow_research,
        inputs=job_id,
        outputs=[
            progress,
            status,
            answer,
            sources,
            error,
        ],
    )


    new_button.click(
        reset_research,
        outputs=[
            job_id,
            status,
            progress,
            answer,
            sources,
            error,
        ],
    )


# ---------------------------------------------------------------------------
# Launch
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    demo.launch(
        css=CSS,
        theme=gr.themes.Base(),
        server_name="0.0.0.0",
        server_port=int(
            os.getenv("PORT", "7860")
        ),
    )