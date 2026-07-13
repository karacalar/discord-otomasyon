"""Import smoke tests."""

def test_core_imports() -> None:
    import bot.client  # noqa: F401
    import dashboard.app  # noqa: F401
    import database.models  # noqa: F401
    import services.repository  # noqa: F401
