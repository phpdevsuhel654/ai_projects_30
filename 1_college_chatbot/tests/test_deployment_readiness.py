from pathlib import Path

from app import create_app


def test_production_config_security_flags():
    app = create_app("production", {"AUTO_CREATE_TABLES": False})

    assert app.config["DEBUG"] is False
    assert app.config["SESSION_COOKIE_SECURE"] is True
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"


def test_deployment_files_exist():
    root = Path(__file__).resolve().parents[1]

    assert (root / "wsgi.py").exists()
    assert (root / "Dockerfile").exists()
    assert (root / "docker-compose.yml").exists()
    assert (root / "docs" / "deployment.md").exists()
    assert (root / ".github" / "workflows" / "ci.yml").exists()
    assert (root / "docs" / "ci_cd.md").exists()
    assert (root / "docs" / "runbook.md").exists()
    assert (root / "docs" / "release_checklist.md").exists()
    assert (root / "docs" / "project_walkthrough.md").exists()
