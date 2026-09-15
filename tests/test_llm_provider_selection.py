import os
import unittest
from unittest.mock import Mock, patch


class LLMProviderSelectionTests(unittest.TestCase):
    def setUp(self):
        self._original_env = dict(os.environ)
        for key in [
            "LLM_PROVIDER",
            "OPEN_ROUTER",
            "OPENROUTER_API_KEY",
            "OPENAI_API_KEY",
            "XKIRO_API_KEY",
            "OLLAMA_ENDPOINT",
        ]:
            os.environ.pop(key, None)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._original_env)

    def test_default_provider_uses_fallback_when_key_present(self):
        os.environ["OPENROUTER_API_KEY"] = "test-key"

        from app.LLM import get_llm

        llm = get_llm("openrouter/free")
        self.assertEqual(type(llm).__name__, "FallbackLLM")

    def test_openrouter_accepts_standard_env_name(self):
        os.environ["OPENROUTER_API_KEY"] = "test-key"

        from app.LLM.openrouter import OpenRouterLLM

        llm = OpenRouterLLM("openrouter/free")
        self.assertEqual(llm.api_key, "test-key")

    def test_default_provider_uses_fallback_when_xkiro_key_present(self):
        os.environ["XKIRO_API_KEY"] = "test-key"

        from app.LLM import get_llm

        llm = get_llm("openai/gpt-5.6-sol")
        self.assertEqual(type(llm).__name__, "FallbackLLM")

    def test_xkiro_is_primary_provider_in_fallback_chain(self):
        os.environ["XKIRO_API_KEY"] = "test-key"
        os.environ["OPENROUTER_API_KEY"] = "test-key"

        from app.LLM import get_llm

        llm = get_llm("openai/gpt-5.6-sol", provider="fallback")
        self.assertEqual(type(llm.providers[0]).__name__, "XkiroLLM")
        self.assertEqual(type(llm.providers[1]).__name__, "OpenRouterLLM")
        self.assertEqual(type(llm.providers[2]).__name__, "OllamaLLM")

    def test_xkiro_provider_can_be_selected_explicitly(self):
        os.environ["XKIRO_API_KEY"] = "test-key"

        from app.LLM import get_llm

        llm = get_llm("openai/gpt-5.6-sol", provider="xkiro")
        self.assertEqual(type(llm).__name__, "XkiroLLM")

    def test_xkiro_accepts_standard_env_name(self):
        os.environ["XKIRO_API_KEY"] = "test-key"

        from app.LLM.xkiro import XkiroLLM

        llm = XkiroLLM("openai/gpt-5.6-sol")
        self.assertEqual(llm.api_key, "test-key")

    def test_xkiro_missing_key_raises_actionable_error(self):
        from app.LLM.xkiro import XkiroLLM, XkiroError

        with self.assertRaisesRegex(XkiroError, "XKIRO_API_KEY"):
            XkiroLLM("openai/gpt-5.6-sol")

    @patch("app.LLM.xkiro.httpx.Client")
    def test_xkiro_sends_openai_compatible_chat_request(self, client_class):
        response = Mock()
        response.is_error = False
        response.json.return_value = {
            "choices": [{"message": {"role": "assistant", "content": "hello from xkiro"}}]
        }
        response.raise_for_status.return_value = None
        mock_post = client_class.return_value.post
        mock_post.return_value = response

        os.environ["XKIRO_API_KEY"] = "test-key"

        from app.LLM.xkiro import XkiroLLM

        llm = XkiroLLM("openai/gpt-5.6-sol")
        result = llm.generate("Say hello")

        self.assertEqual(result, "hello from xkiro")
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "chat/completions")
        self.assertEqual(kwargs["json"]["model"], "openai/gpt-5.6-sol")
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test-key")

    @patch("app.LLM.xkiro.httpx.Client")
    def test_xkiro_surfaces_http_error_body(self, client_class):
        # The API's JSON error body explains why a model is unavailable (e.g. a
        # premium model blocked for accounts on promotional credit), so it must
        # surface instead of the generic "Client error '403 Forbidden'".
        response = Mock()
        response.is_error = True
        response.status_code = 403
        response.text = '{"error":{"message":"premium model needs a paid plan"}}'
        client_class.return_value.post.return_value = response

        os.environ["XKIRO_API_KEY"] = "test-key"

        from app.LLM.xkiro import XkiroError, XkiroLLM

        llm = XkiroLLM("qwen/qwen3.5-plus:free")
        with self.assertRaisesRegex(XkiroError, r"HTTP 403.*paid plan"):
            llm.generate("hi")

    def test_fallback_routes_xkiro_to_free_model_default(self):
        os.environ["XKIRO_API_KEY"] = "test-key"

        from app.LLM import get_llm
        from app.LLM.router import XKIRO_DEFAULT_MODEL

        llm = get_llm("openrouter/free")
        self.assertEqual(type(llm.providers[0]).__name__, "XkiroLLM")
        # xKiro cannot serve the shared "openrouter/free" default, so it receives
        # a free-tier xKiro model id instead.
        self.assertEqual(llm.providers[0].model, XKIRO_DEFAULT_MODEL)
        self.assertNotEqual(llm.providers[0].model, "openrouter/free")

    def test_fallback_honors_explicit_vendor_model(self):
        os.environ["XKIRO_API_KEY"] = "test-key"

        from app.LLM import get_llm

        # Explicit xKiro model ids pass through unchanged; only the app's shared
        # OpenRouter-flavoured default is substituted with the free xKiro model.
        llm = get_llm("qwen/qwen3.5-plus:free")
        self.assertEqual(llm.providers[0].model, "qwen/qwen3.5-plus:free")

    def test_xkiro_explicit_selection_resolves_to_free_default(self):
        os.environ["XKIRO_API_KEY"] = "test-key"

        from app.LLM import get_llm
        from app.LLM.router import XKIRO_DEFAULT_MODEL

        llm = get_llm("openrouter/free", provider="xkiro")
        self.assertEqual(type(llm).__name__, "XkiroLLM")
        self.assertEqual(llm.model, XKIRO_DEFAULT_MODEL)

    def test_xkiro_honors_explicit_vendor_model(self):
        os.environ["XKIRO_API_KEY"] = "test-key"

        from app.LLM import get_llm

        llm = get_llm("qwen/qwen3.5-plus:free", provider="xkiro")
        self.assertEqual(type(llm).__name__, "XkiroLLM")
        self.assertEqual(llm.model, "qwen/qwen3.5-plus:free")

    def test_unknown_provider_has_actionable_error(self):
        from app.LLM import get_llm

        with self.assertRaisesRegex(ValueError, "Supported"):
            get_llm("model", provider="unknown")

    def test_fallback_moves_past_empty_provider_responses(self):
        from app.LLM.router import FallbackLLM

        class Provider:
            def __init__(self, value):
                self.value = value
                self.calls = 0

            def generate(self, prompt):
                self.calls += 1
                if callable(self.value):
                    raise self.value
                return self.value

        provider_a = Provider("")
        provider_b = Provider("real answer")
        llm = FallbackLLM("model", providers=[provider_a, provider_b])

        self.assertEqual(llm.generate("prompt"), "real answer")
        self.assertEqual(provider_a.calls, 1)
        self.assertEqual(provider_b.calls, 1)

    def test_fallback_raises_when_every_provider_degraded(self):
        from app.LLM.router import FallbackLLM

        class EmptyProvider:
            def generate(self, prompt):
                return "   "

        llm = FallbackLLM("model", providers=[EmptyProvider(), EmptyProvider()])

        with self.assertRaisesRegex(RuntimeError, "usable response"):
            llm.generate("prompt")

    def test_fallback_retries_next_provider_once_one_raises(self):
        from app.LLM.router import FallbackLLM

        class Raising:
            def generate(self, prompt):
                raise RuntimeError("provider down")

        llm = FallbackLLM("model", providers=[Raising(), Raising()])

        with self.assertRaisesRegex(RuntimeError, "provider down"):
            llm.generate("prompt")


if __name__ == "__main__":
    unittest.main()
