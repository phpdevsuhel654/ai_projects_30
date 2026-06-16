from app.models.chat_history import ChatHistory
from app.models.faq_category import FAQCategory
from app.models.knowledge_base import KnowledgeBase
from app.models.student_query import StudentQuery
from app.models.user import User

__all__ = [
	"User",
	"FAQCategory",
	"KnowledgeBase",
	"StudentQuery",
	"ChatHistory",
]
