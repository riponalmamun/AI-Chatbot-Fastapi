from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "AI Chatbot API")
    app_env: str = os.getenv("APP_ENV", "dev")
    debug: bool = os.getenv("APP_DEBUG", "true").lower() == "true"
    host: str = os.getenv("APP_HOST", "0.0.0.0")
    port: int = int(os.getenv("APP_PORT", "8000"))

    llm_provider: str = os.getenv("LLM_PROVIDER", "groq")
    groq_api_key: str | None = os.getenv("GROQ_API_KEY")
    groq_model: str = os.getenv("GROQ_MODEL", "llama3-70b-8192")
    max_tokens: int = int(os.getenv("MAX_TOKENS", 512))
    temperature: float = float(os.getenv("TEMPERATURE", 0.7))

settings = Settings()