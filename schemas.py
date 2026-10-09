
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": (
                "Search CampusConnect's local FAQ knowledge base. "
                "Use this first for general support questions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's support question or search terms."
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_policy_details",
            "description": (
                "Retrieve documented CampusConnect policy details. "
                "Use this for refund, payment, application, or account policies."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "policy_name": {
                        "type": "string",
                        "description": (
                            "Policy to look up, such as refunds, payments, "
                            "applications, or accounts."
                        )
                    }
                },
                "required": ["policy_name"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_support_ticket",
            "description": (
                "Create a persistent support ticket for an unresolved "
                "issue or a problem requiring staff review."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "issue": {
                        "type": "string",
                        "description": "A concise description of the user's issue."
                    },
                    "category": {
                        "type": "string",
                        "description": (
                            "Issue category, such as payment, account, "
                            "application, refund, or general."
                        )
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Priority based on the issue's urgency."
                    }
                },
                "required": ["issue", "category", "priority"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_human",
            "description": (
                "Escalate an existing support ticket when it needs "
                "human review. A ticket must be created first."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "The existing CampusConnect ticket ID."
                    },
                    "reason": {
                        "type": "string",
                        "description": "Why human review is needed."
                    }
                },
                "required": ["ticket_id", "reason"],
                "additionalProperties": False
            }
        }
    }
]
