import os
import unittest


class LLMProviderSelectionTests(unittest.TestCase):
    def setUp(self):
        self._original_env = dict(os.environ)
        for key in [
            "LLM_PROVIDER",
            "OPEN_ROUTER",
            "OPENROUTER_API_KEY",
            "OPENAI_API_KEY",
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
