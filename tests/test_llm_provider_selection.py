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


if __name__ == "__main__":
    unittest.main()
