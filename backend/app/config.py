"""Instellingen van de app, gelezen uit omgevingsvariabelen of uit het bestand .env.

Geheimen (wachtwoorden, sleutels, connection strings) staan nooit in de code.
Lokaal staan ze in .env (gitignored, zie .env.example). In productie komen ze uit
Azure Key Vault en worden ze via de omgeving van de App Service aangeleverd.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Eén instelling voor de database: SQLite lokaal, Azure SQL in productie.
    database_url: str = "sqlite:///./lokalen.db"

    # CORS-allowlist: alleen deze websites mogen de API vanuit de browser aanroepen.
    cors_origins: list[str] = ["http://localhost:5173"]

    # Gelezen uit de omgevingsvariabele APP_VERSION.
    # De CI-pipeline zet die bij elke build (bijvoorbeeld "142-a1b2c3d"), zodat
    # GET /version bewijst welke build er echt draait.
    app_version: str = "dev"

    # Testlogin via de header X-Dev-User. In productie staat dit uit.
    dev_auth_enabled: bool = True


settings = Settings()
