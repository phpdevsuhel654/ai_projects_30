from app.extensions import db
from app.models.faq_category import FAQCategory
from app.models.knowledge_base import KnowledgeBase
from app.models.user import User


def _create_user(app, email, role):
    with app.app_context():
        user = User(full_name="Test User", email=email, role=role)
        user.set_password("secret123")
        db.session.add(user)
        db.session.commit()


def _login(client, email):
    return client.post(
        "/auth/login",
        data={"email": email, "password": "secret123"},
        follow_redirects=True,
    )


def test_admin_dashboard_requires_admin_role(app, client):
    _create_user(app, "student@example.com", "student")
    _login(client, "student@example.com")

    response = client.get("/admin/", follow_redirects=True)

    assert response.status_code == 200
    assert b"Admin access required" in response.data


def test_admin_can_create_category_and_knowledge(app, client):
    _create_user(app, "admin@example.com", "admin")
    _login(client, "admin@example.com")

    response = client.post(
        "/admin/categories",
        data={"name": "Scholarships", "description": "Aid related queries"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        category = FAQCategory.query.filter_by(name="Scholarships").first()
        assert category is not None

    response = client.post(
        "/admin/knowledge",
        data={
            "title": "Scholarship Eligibility",
            "content": "Scholarships are based on merit and category.",
            "category_id": str(category.id),
            "tags": "scholarship merit",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        item = KnowledgeBase.query.filter_by(title="Scholarship Eligibility").first()
        assert item is not None
