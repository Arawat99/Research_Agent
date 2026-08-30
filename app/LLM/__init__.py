'''Top‑level package for LLM abstractions.

The public API consists of the :func:`get_llm` factory which returns an
instance of a concrete LLM provider implementing the :class:`app.LLM.base.LLMBase`
interface.  Importing ``app.LLM`` is therefore sufficient for callers:

    from app.LLM import get_llm
    llm = get_llm(model="gpt-oss:120b-cloud")

Additional convenience re‑exports are provided for type checking.
'''  # noqa: D400

from .base import LLMBase
from .router import get_llm

__all__ = ["LLMBase", "get_llm"]
