from app.extensions import db
from app.models.faq_category import FAQCategory
from app.models.knowledge_base import KnowledgeBase


def seed_phase1_knowledge_base():
    if KnowledgeBase.query.first():
        return

    general = FAQCategory(name="General", description="General college info")
    admissions = FAQCategory(name="Admissions", description="Admission process details")
    fees = FAQCategory(name="Fees", description="Fee structure details")

    db.session.add_all([general, admissions, fees])
    db.session.flush()

    entries = [
        KnowledgeBase(
            category_id=admissions.id,
            title="Admission Process",
            content="Admissions are open from June to August. Submit the online form and required documents.",
            tags="admission apply process eligibility",
            is_published=True,
        ),
        KnowledgeBase(
            category_id=fees.id,
            title="Fee Structure",
            content="Annual tuition fees vary by program. Contact accounts@college.edu for exact breakdown.",
            tags="fee fees tuition payment cost",
            is_published=True,
        ),
        KnowledgeBase(
            category_id=general.id,
            title="Hostel Information",
            content="Separate hostel facilities are available for boys and girls with mess and Wi-Fi.",
            tags="hostel accommodation rooms mess",
            is_published=True,
        ),
        KnowledgeBase(
            category_id=general.id,
            title="Placements",
            content="The placement cell supports internships and final placements with partner companies.",
            tags="placement placements jobs internship",
            is_published=True,
        ),
    ]

    db.session.add_all(entries)
    db.session.commit()
