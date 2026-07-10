def _create_cron(client, name="Report Cron"):
    payload = {
        "name": name,
        "url": "https://example.com/cron",
        "execution_count": 1,
        "schedule_type": "daily",
    }
    response = client.post("/api/cron", json=payload)
    assert response.status_code == 201
    return response.get_json()


def test_report_trend_endpoint(client):
    cron = _create_cron(client)
    client.post(f"/api/run/{cron['id']}")

    response = client.get("/api/report/trend?days=7")
    assert response.status_code == 200
    payload = response.get_json()
    assert "items" in payload


def test_report_error_summary_endpoint(client):
    _create_cron(client)

    response = client.get("/api/report/errors?period=daily&limit=5")
    assert response.status_code == 200
    payload = response.get_json()
    assert "items" in payload


def test_report_csv_export(client):
    cron = _create_cron(client)
    client.post(f"/api/run/{cron['id']}")

    response = client.get("/api/report/export?period=daily")
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert "cron_job_id" in response.get_data(as_text=True)


def test_reports_page_shows_phase4_sections(client):
    response = client.get("/reports")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Trend" in html
    assert "Top Errors" in html
