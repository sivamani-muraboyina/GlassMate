from app.core.config import Settings
from app.db.session import create_database_engine


def test_database_configuration_can_be_loaded() -> None:
    settings = Settings(database_url="postgresql+psycopg://user:password@localhost:5432/glassmate")

    assert settings.app_name == "GlassMate"
    assert settings.database_url.startswith("postgresql+psycopg://")


def test_database_engine_is_constructed_without_connecting() -> None:
    settings = Settings(database_url="sqlite://")

    engine = create_database_engine(settings)

    assert str(engine.url) == "sqlite://"
