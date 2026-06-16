from flask import redirect, render_template, request, url_for
from flask_login import login_required

from app.admin import admin_bp
from app.extensions import db
from app.models.chat_history import ChatHistory
from app.models.faq_category import FAQCategory
from app.models.knowledge_base import KnowledgeBase
from app.models.student_query import StudentQuery
from app.models.user import User
from app.utils.authz import admin_required


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    stats = {
        "users": db.session.query(User).count(),
        "categories": db.session.query(FAQCategory).count(),
        "knowledge_items": db.session.query(KnowledgeBase).count(),
        "queries": db.session.query(StudentQuery).count(),
        "chat_records": db.session.query(ChatHistory).count(),
    }
    return render_template("admin/dashboard.html", stats=stats)


@admin_bp.route("/categories", methods=["GET", "POST"])
@login_required
@admin_required
def categories():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        if name and not FAQCategory.query.filter_by(name=name).first():
            db.session.add(FAQCategory(name=name, description=description or None))
            db.session.commit()
        return redirect(url_for("admin.categories"))

    data = FAQCategory.query.order_by(FAQCategory.name.asc()).all()
    return render_template("admin/categories.html", categories=data)


@admin_bp.route("/categories/<int:category_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_category(category_id):
    category = db.session.get(FAQCategory, category_id)
    if category:
        db.session.delete(category)
        db.session.commit()
    return redirect(url_for("admin.categories"))


@admin_bp.route("/knowledge", methods=["GET", "POST"])
@login_required
@admin_required
def knowledge():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        category_id = request.form.get("category_id", "").strip()
        tags = request.form.get("tags", "").strip()

        if title and content:
            item = KnowledgeBase(
                title=title,
                content=content,
                tags=tags or None,
                category_id=int(category_id) if category_id else None,
                is_published=True,
            )
            db.session.add(item)
            db.session.commit()

        return redirect(url_for("admin.knowledge"))

    categories_data = FAQCategory.query.order_by(FAQCategory.name.asc()).all()
    items = KnowledgeBase.query.order_by(KnowledgeBase.id.desc()).all()
    return render_template(
        "admin/knowledge.html",
        categories=categories_data,
        items=items,
    )


@admin_bp.route("/knowledge/<int:item_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_knowledge(item_id):
    item = db.session.get(KnowledgeBase, item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for("admin.knowledge"))
