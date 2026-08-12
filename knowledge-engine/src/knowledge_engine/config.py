"""Configuration loaded from .env — see .env.example for the required keys."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(
            f"Missing {name}. Copy .env.example to .env and fill it in "
            "(see docs/BEFORE-YOU-START.md)."
        )
    return value


class Settings:
    @property
    def st_client_id(self) -> str: return _require("ST_CLIENT_ID")
    @property
    def st_client_secret(self) -> str: return _require("ST_CLIENT_SECRET")
    @property
    def st_app_key(self) -> str: return _require("ST_APP_KEY")
    @property
    def st_tenant_id(self) -> str: return _require("ST_TENANT_ID")
    @property
    def anthropic_api_key(self) -> str: return _require("ANTHROPIC_API_KEY")

    @property
    def data_dir(self) -> Path:
        d = Path(os.environ.get("KE_DATA_DIR", "./data"))
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def db_path(self) -> Path:
        return self.data_dir / "knowledge.db"


settings = Settings()
