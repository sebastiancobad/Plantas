"""
ChemScale Application Configuration.

Central configuration management using Pydantic Settings.
All environment variables are loaded here and made available
to the entire application through the `settings` singleton.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "ChemScale"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql://chemscale:chemscale@localhost:5432/chemscale"

    # Redis (caching thermodynamic lookups)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery (heavy async computations)
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Computation limits
    MAX_ITERATION_COUNT: int = 500
    CONVERGENCE_TOLERANCE: float = 1e-6

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
