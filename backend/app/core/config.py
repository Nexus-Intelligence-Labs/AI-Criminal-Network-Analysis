from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ==========================================
    # Application
    # ==========================================
    app_env: str = "development"
    app_name: str = "AI Criminal Network Analysis API"

    # ==========================================
    # PostgreSQL
    # ==========================================
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "criminal_network"
    postgres_user: str = "postgres"
    postgres_password: str = ""

    # ==========================================
    # Neo4j
    # ==========================================
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""

    # ==========================================
    # Backend
    # ==========================================
    backend_host: str = "127.0.0.1"
    backend_port: int = 8000

    # ==========================================
    # Frontend
    # ==========================================
    vite_api_base_url: str = "http://localhost:8000"

    # ==========================================
    # Security
    # ==========================================
    jwt_secret: str = "change_me"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()

