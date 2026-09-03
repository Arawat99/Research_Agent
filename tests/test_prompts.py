import tempfile
import unittest
from pathlib import Path

from app.prompts.loader import add_system_prompt, load_prompts


class PromptLoaderTests(unittest.TestCase):
    def test_loads_supported_prompt_files_in_filename_order(self):
        with tempfile.TemporaryDirectory() as directory:
            prompt_dir = Path(directory)
            (prompt_dir / "z-last.txt").write_text("last", encoding="utf-8")
            (prompt_dir / "a-first.md").write_text("first", encoding="utf-8")
            (prompt_dir / "ignored.py").write_text("ignored", encoding="utf-8")

            self.assertEqual(load_prompts(prompt_dir), "first\n\nlast")

    def test_add_system_prompt_keeps_task_after_instructions(self):
        result = add_system_prompt("Answer the question.", "Follow these rules.")

        self.assertEqual(
            result,
            "=== SYSTEM INSTRUCTIONS ===\n"
            "Follow these rules.\n\n"
            "=== TASK ===\n"
            "Answer the question.",
        )


if __name__ == "__main__":
    unittest.main()
