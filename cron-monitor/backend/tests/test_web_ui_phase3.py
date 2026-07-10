def test_dashboard_page_loads(client):
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"Execution Dashboard" in response.data


def test_cron_jobs_page_loads(client):
    response = client.get("/cron-jobs")
    assert response.status_code == 200
    assert b"Add Cron Job" in response.data


def test_create_cron_job_from_web_form(client):
    form_data = {
        "name": "Web Cron",
        "url": "https://example.com/cron",
        "execution_count": "1",
        "schedule_type": "daily",
        "schedule_expression": "",
        "description": "created from web",
        "is_active": "on",
    }

    response = client.post("/cron-jobs", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Cron job added successfully." in response.data
    assert b"Web Cron" in response.data


def test_edit_cron_job_from_web_form(client):
    create_data = {
        "form_mode": "create",
        "name": "Editable Cron",
        "url": "https://example.com/old",
        "execution_count": "1",
        "schedule_type": "daily",
        "schedule_expression": "",
        "description": "old description",
        "is_active": "on",
    }
    create_response = client.post("/cron-jobs", data=create_data, follow_redirects=True)
    assert create_response.status_code == 200

    list_response = client.get("/api/cron")
    jobs = list_response.get_json()
    target = next(item for item in jobs if item["name"] == "Editable Cron")

    update_data = {
        "form_mode": "edit",
        "cron_id": str(target["id"]),
        "name": "Edited Cron",
        "url": "https://example.com/new",
        "execution_count": "2",
        "schedule_type": "hourly",
        "schedule_expression": "",
        "description": "updated description",
    }

    update_response = client.post("/cron-jobs", data=update_data, follow_redirects=True)
    assert update_response.status_code == 200
    assert b"Cron job updated successfully." in update_response.data
    assert b"Edited Cron" in update_response.data
