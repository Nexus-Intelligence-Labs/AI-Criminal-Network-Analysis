from functools import lru_cache

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Allowed JWT signing algorithms.  The server must control which algorithms
# are accepted during verification — never trust client-supplied algorithm
# negotiation.  Only HS256 is supported at this stage.
ALLOWED_JWT_ALGORITHMS = {"HS256"}

# Known insecure placeholder secrets that must never be used in production.
INSECURE_PLACEHOLDER_SECRETS = {
    "change_me",
    "changeme",
    "secret",
    "password",
    "change_me_to_a_longer_production_secret",
}

# Minimum JWT secret length (in bytes) for HMAC-SHA256.
MIN_JWT_SECRET_BYTES = 32

# Reasonable upper bound for access token lifetime (in minutes).
# 7 days = 10080 minutes.  Anything larger is almost certainly a misconfiguration.
MAX_JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 10080


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "AI Criminal Network Analysis API"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "criminal_network"
    postgres_user: str = "postgres"
    postgres_password: str = ""
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""
    backend_host: str = "127.0.0.1"
    backend_port: int = 8000
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(env_file=None, case_sensitive=False)

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret_not_empty(cls, v: str) -> str:
        """JWT secret must be non-empty and at least 32 bytes."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("JWT_SECRET must not be empty")
        if len(v.encode("utf-8")) < 32:
            raise ValueError("JWT_SECRET must be at least 32 bytes")
        return v

    @model_validator(mode="after")
    def validate_production_secret(self) -> "Settings":
        """In production, the JWT secret must not be a known placeholder."""
        if self.app_env == "production":
            if self.jwt_secret.strip().lower() in INSECURE_PLACEHOLDER_SECRETS:
                raise ValueError(
                    "JWT_SECRET must not be a known insecure placeholder in production"
                )
        return self

    @field_validator("jwt_algorithm")
    @classmethod
    def validate_jwt_algorithm(cls, v: str) -> str:
        """JWT algorithm must be in the server-controlled allowlist."""
        if v not in ALLOWED_JWT_ALGORITHMS:
            raise ValueError(
                f"JWT_ALGORITHM must be one of {sorted(ALLOWED_JWT_ALGORITHMS)}"
            )
        return v

    @field_validator("jwt_access_token_expire_minutes")
    @classmethod
    def validate_jwt_expire_minutes(cls, v: int) -> int:
        """Access token lifetime must be positive and within a sane bound."""
        if v <= 0:
            raise ValueError("JWT_ACCESS_TOKEN_EXPIRE_MINUTES must be positive")
        if v > MAX_JWT_ACCESS_TOKEN_EXPIRE_MINUTES:
            raise ValueError(
                f"JWT_ACCESS_TOKEN_EXPIRE_MINUTES must not exceed "
                f"{MAX_JWT_ACCESS_TOKEN_EXPIRE_MINUTES}"
            )
        return v

    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()