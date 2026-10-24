from fastapi.testclient import TestClient


def test_health_returns_ok_without_database(monkeypatch):
    """Liveness must work without PostgreSQL or a developer's .env file."""
    test_settings = {
        "POSTGRES_DB": "policy_rag_test",
        "POSTGRES_USER": "policy_rag_test",
        "POSTGRES_PASSWORD": "test-only-not-a-real-credential",
        "POSTGRES_HOST": "127.0.0.1",
        "POSTGRES_PORT": "5432",
    }
    for name, value in test_settings.items():
        monkeypatch.setenv(name, value)

    # Settings are currently created when main is imported.
    # Set test variables before importing the application.
    import psycopg
    from main import app

    def unexpected_database_connection(*args, **kwargs):
        raise AssertionError("/health must not connect to PostgreSQL")

    monkeypatch.setattr(psycopg, "connect", unexpected_database_connection)

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
