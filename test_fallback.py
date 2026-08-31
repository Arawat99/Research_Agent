import os
from dotenv import load_dotenv

# Load environment variables from .env file located in the project root
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

# Ensure the fallback provider is selected
os.environ["LLM_PROVIDER"] = "fallback"

from app.LLM import get_llm

# Use a model identifier that OpenRouter recognises. Adjust if needed.
model_name = "openrouter/free"

llm = get_llm(model=model_name)

prompt = "What is the capital of France?"

try:
    answer = llm.generate(prompt)
    print("Answer:", answer)
except Exception as e:
    print("Failed to get answer:", e)
