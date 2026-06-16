from app.chatbot.nlp_engine import NLPEngine


def test_intent_detection_for_fees():
    result = NLPEngine().analyze("What is the fee for BCA in 2026?")
    assert result["intent"] == "fee_structure"


def test_entity_extraction_program_and_year():
    result = NLPEngine().analyze("Need hostel details for BTech 2027")
    assert result["entities"].get("program") == "BTECH"
    assert result["entities"].get("year") == "2027"
