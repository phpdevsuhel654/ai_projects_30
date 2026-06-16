import json

from app.extensions import db
from app.models.chat_history import ChatHistory
from app.models.student_query import StudentQuery


class ChatRepository:
    @staticmethod
    def get_recent_history(session_id, limit=4):
        records = (
            db.session.query(ChatHistory)
            .filter_by(session_id=session_id)
            .order_by(ChatHistory.id.desc())
            .limit(limit)
            .all()
        )
        return list(reversed(records))

    @staticmethod
    def save_interaction(
        user_id,
        query_text,
        detected_intent,
        entities,
        session_id,
        response_text,
        source,
        confidence,
    ):
        query = StudentQuery(
            user_id=user_id,
            query_text=query_text,
            detected_intent=detected_intent,
            entities_json=json.dumps(entities or {}),
        )
        db.session.add(query)
        db.session.flush()

        record = ChatHistory(
            user_id=user_id,
            query_id=query.id,
            session_id=session_id,
            user_message=query_text,
            bot_response=response_text,
            response_source=source,
            confidence_score=confidence,
        )
        db.session.add(record)
        db.session.commit()

        return record
