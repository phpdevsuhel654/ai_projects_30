from app import create_app


def test_create_app_with_testing_config():
    app = create_app("testing")
    assert app.config["TESTING"] is True


def test_home_page_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200
