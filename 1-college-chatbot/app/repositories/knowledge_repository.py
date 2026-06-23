from app.models.knowledge_base import KnowledgeBase


class KnowledgeRepository:
    @staticmethod
    def get_published_entries(limit=200):
        return (
            KnowledgeBase.query.filter_by(is_published=True)
            .order_by(KnowledgeBase.id.asc())
            .limit(limit)
            .all()
        )
