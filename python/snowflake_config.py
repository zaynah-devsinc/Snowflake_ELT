#!/usr/bin/env python3
import os
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

ROOT_DIR = Path(__file__).resolve().parent.parent
SECRETS_PATH = ROOT_DIR / ".streamlit" / "secrets.toml"
DEFAULT_DATABASE = "ELT_WAREHOUSE"
DEFAULT_SCHEMA = "RAW_MARTS"


def _load_streamlit_secrets() -> dict[str, str]:
    if not SECRETS_PATH.exists():
        return {}

    with SECRETS_PATH.open("rb") as fh:
        payload = tomllib.load(fh)

    snowflake_block = payload.get("snowflake", {}) or {}
    return {k: str(v) for k, v in snowflake_block.items() if v is not None}


def load_snowflake_config() -> dict[str, str | None]:
    config = {
        "user": os.getenv("SNOWFLAKE_USER"),
        "password": os.getenv("SNOWFLAKE_PASSWORD"),
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database": os.getenv("SNOWFLAKE_DATABASE", DEFAULT_DATABASE),
        "schema": os.getenv("SNOWFLAKE_SCHEMA", DEFAULT_SCHEMA),
        "role": os.getenv("SNOWFLAKE_ROLE"),
    }

    if SECRETS_PATH.exists():
        secrets = _load_streamlit_secrets()
        config.update({
            "user": config["user"] or secrets.get("user"),
            "password": config["password"] or secrets.get("password"),
            "account": config["account"] or secrets.get("account"),
            "warehouse": config["warehouse"] or secrets.get("warehouse"),
            "database": config["database"] or secrets.get("database", DEFAULT_DATABASE),
            "schema": config["schema"] or secrets.get("schema", DEFAULT_SCHEMA),
            "role": config["role"] or secrets.get("role"),
        })

    return config


def has_snowflake_config(config: dict[str, str | None]) -> bool:
    return all(config.get(key) for key in ("user", "password", "account", "warehouse"))


def validate_snowflake_config(config: dict[str, str | None]) -> dict[str, str]:
    required = ["user", "password", "account", "warehouse"]
    missing = [key for key in required if not config.get(key)]
    if missing:
        raise ValueError("Missing Snowflake config: " + ", ".join(missing))
    return config  # type: ignore[return-value]
