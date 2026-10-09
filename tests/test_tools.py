
import pytest
import tools


def test_search_knowledge_base():
    result = tools.search_knowledge_base("reset password")

    assert result["success"] is True
    assert result["count"] > 0
    assert any(
        "password" in item["question"].lower()
        for item in result["results"]
    )


def test_search_empty_query():
    result = tools.search_knowledge_base("")

    assert result["success"] is False


def test_search_no_matching_results():
    result = tools.search_knowledge_base(
        "xyzunknownquestion987"
    )

    assert result["success"] is True
    assert result["count"] == 0


def test_get_refund_policy():
    result = tools.get_policy_details("refund")

    assert result["success"] is True


def test_unknown_policy():
    result = tools.get_policy_details(
        "unknown_policy_xyz"
    )

    assert result["success"] is False


def test_create_ticket_and_escalate(tmp_path, monkeypatch):
    # Use a temporary database so tests don't modify
    # the application's actual support.db file.
    monkeypatch.setattr(
        tools,
        "DATA_DIR",
        tmp_path
    )
    monkeypatch.setattr(
        tools,
        "DATABASE_FILE",
        tmp_path / "test_support.db"
    )

    ticket = tools.create_support_ticket(
        issue="Payment deducted but application is unpaid",
        category="payment",
        priority="high"
    )

    assert ticket["success"] is True
    assert ticket["ticket_id"].startswith("CC-")
    assert ticket["status"] == "open"

    escalation = tools.escalate_to_human(
        ticket_id=ticket["ticket_id"],
        reason="Payment requires human review"
    )

    assert escalation["success"] is True
    assert escalation["ticket_id"] == ticket["ticket_id"]
    assert escalation["status"] == "escalated"


def test_create_ticket_rejects_empty_issue():
    result = tools.create_support_ticket(
        issue="",
        category="general",
        priority="medium"
    )

    assert result["success"] is False


def test_create_ticket_rejects_invalid_priority():
    result = tools.create_support_ticket(
        issue="Test issue",
        category="general",
        priority="urgent"
    )

    assert result["success"] is False


def test_escalate_unknown_ticket():
    result = tools.escalate_to_human(
        ticket_id="CC-UNKNOWN123",
        reason="Test escalation"
    )

    assert result["success"] is False
