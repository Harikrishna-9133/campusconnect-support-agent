
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_FILE = DATA_DIR / "knowledge_base.json"
POLICIES_FILE = DATA_DIR / "policies.json"
DATABASE_FILE = DATA_DIR / "support.db"


def load_json_file(file_path):
    """Load a local JSON file with graceful error handling."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return None
    except (json.JSONDecodeError, OSError):
        return None


def search_knowledge_base(query):
    """Search documented FAQs using words from the question."""
    if not isinstance(query, str) or not query.strip():
        return {
            "success": False,
            "error": "Please provide a non-empty search query."
        }

    knowledge = load_json_file(KNOWLEDGE_FILE)

    if not knowledge or not isinstance(knowledge.get("faqs"), list):
        return {
            "success": False,
            "error": "The knowledge base is unavailable."
        }

    words = {
        word.lower().strip(".,?!")
        for word in query.split()
        if len(word) > 2
    }

    results = []

    for faq in knowledge["faqs"]:
        searchable_text = " ".join([
            faq.get("question", ""),
            faq.get("answer", ""),
            " ".join(faq.get("keywords", []))
        ]).lower()

        score = sum(
            1 for word in words if word in searchable_text
        )

        if score > 0:
            results.append({
                "id": faq.get("id"),
                "question": faq.get("question"),
                "answer": faq.get("answer"),
                "score": score
            })

    results.sort(key=lambda item: item["score"], reverse=True)

    return {
        "success": True,
        "query": query,
        "results": results[:5],
        "count": len(results)
    }


def get_policy_details(policy_name):
    """Retrieve a documented policy by name or keyword."""
    if not isinstance(policy_name, str) or not policy_name.strip():
        return {
            "success": False,
            "error": "Please specify which policy you need."
        }

    policies = load_json_file(POLICIES_FILE)

    if not isinstance(policies, dict):
        return {
            "success": False,
            "error": "The policy file is unavailable."
        }

    query = policy_name.lower().strip()

    matches = []

    for key, policy in policies.items():
        searchable_text = (
            key + " " +
            policy.get("title", "") + " " +
            policy.get("details", "")
        ).lower()

        if query in key.lower() or query in searchable_text:
            matches.append({
                "key": key,
                **policy
            })

    if not matches:
        return {
            "success": False,
            "error": "No matching policy was found."
        }

    return {
        "success": True,
        "policies": matches
    }


def initialize_database():
    """Create the support database and tickets table if needed."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS support_tickets (
                ticket_id TEXT PRIMARY KEY,
                issue TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS escalations (
                escalation_id TEXT PRIMARY KEY,
                ticket_id TEXT NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


def create_support_ticket(issue, category="general", priority="medium"):
    """Create a support ticket and persist it in SQLite."""
    if not isinstance(issue, str) or not issue.strip():
        return {
            "success": False,
            "error": "The issue description cannot be empty."
        }

    if len(issue.strip()) > 2000:
        return {
            "success": False,
            "error": "The issue description is too long (maximum 2000 characters)."
        }

    if not isinstance(category, str) or not category.strip():
        return {
            "success": False,
            "error": "Please provide a valid ticket category."
        }

    allowed_priorities = {"low", "medium", "high"}

    if not isinstance(priority, str) or priority.lower() not in allowed_priorities:
        return {
            "success": False,
            "error": "Priority must be low, medium, or high."
        }

    try:
        initialize_database()

        ticket_id = "CC-" + uuid.uuid4().hex[:8].upper()
        created_at = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(DATABASE_FILE) as connection:
            connection.execute(
                """
                INSERT INTO support_tickets
                (ticket_id, issue, category, priority, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    ticket_id,
                    issue.strip(),
                    category.strip().lower(),
                    priority.lower(),
                    "open",
                    created_at
                )
            )

        return {
            "success": True,
            "ticket_id": ticket_id,
            "issue": issue.strip(),
            "category": category.strip().lower(),
            "priority": priority.lower(),
            "status": "open",
            "created_at": created_at,
            "message": "Support ticket created successfully."
        }

    except sqlite3.Error:
        return {
            "success": False,
            "error": "Unable to save the support ticket."
        }


def escalate_to_human(ticket_id, reason):
    """Record that a ticket needs human review."""
    if not isinstance(ticket_id, str) or not ticket_id.strip():
        return {
            "success": False,
            "error": "A valid ticket ID is required for escalation."
        }

    if not isinstance(reason, str) or not reason.strip():
        return {
            "success": False,
            "error": "Please provide a reason for escalation."
        }

    try:
        initialize_database()

        with sqlite3.connect(DATABASE_FILE) as connection:
            ticket = connection.execute(
                "SELECT ticket_id FROM support_tickets WHERE ticket_id = ?",
                (ticket_id.strip(),)
            ).fetchone()

            if ticket is None:
                return {
                    "success": False,
                    "error": "Ticket not found. Create a ticket first."
                }

            escalation_id = "ESC-" + uuid.uuid4().hex[:8].upper()
            created_at = datetime.now(timezone.utc).isoformat()

            connection.execute(
                """
                INSERT INTO escalations
                (escalation_id, ticket_id, reason, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    escalation_id,
                    ticket_id.strip(),
                    reason.strip(),
                    created_at
                )
            )

            connection.execute(
                "UPDATE support_tickets SET status = ? WHERE ticket_id = ?",
                ("escalated", ticket_id.strip())
            )

        return {
            "success": True,
            "escalation_id": escalation_id,
            "ticket_id": ticket_id.strip(),
            "status": "escalated",
            "message": "The issue has been recorded for human review."
        }

    except sqlite3.Error:
        return {
            "success": False,
            "error": "Unable to record the escalation."
        }


TOOL_FUNCTIONS = {
    "search_knowledge_base": search_knowledge_base,
    "get_policy_details": get_policy_details,
    "create_support_ticket": create_support_ticket,
    "escalate_to_human": escalate_to_human
}
