"""Single-process ASGI application for Render deployment."""

from __future__ import annotations

import os

# Gradio callbacks call the API routes through this same process. Override the
# separate-dev URL from .env before importing the frontend module.
os.environ["RESEARCH_API_URL"] = f"http://127.0.0.1:{os.getenv('PORT', '5000')}"

import gradio as gr

from frontend.app import CSS, demo
from server.main import app as api_app


app = gr.mount_gradio_app(
    api_app,
    demo,
    path="/",
    css=CSS,
    theme=gr.themes.Base(),
)
