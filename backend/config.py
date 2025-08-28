"""
Configuration file for SupplyChainRescue AI backend.
Manages settings for the application including database, APIs, and ML models.
"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application settings
    app_name: str = "SupplyChainRescue AI"
    version: str = "1.0.0"
    api_v1_prefix: str = "/api/v1"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Server settings
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))

    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./supplychain_rescue.db")

    # External API keys
    openweather_api_key: Optional[str] = os.getenv("OPENWEATHER_API_KEY")
    openstreet_map_user_agent: str = os.getenv("OSM_USER_AGENT", "SupplyChainRescueAI/1.0")

    # ML Model settings
    model_cache_dir: str = os.getenv("MODEL_CACHE_DIR", "./models")
    transformer_model_name: str = "t5-base"

    # File paths
    data_dir: str = "./data"
    sample_data_dir: str = "./data/samples"

    # CORS settings
    cors_origins: List[str] = ["*"]  # Configure this for production

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()