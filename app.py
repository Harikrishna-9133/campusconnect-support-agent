
from flask import Flask, render_template, request, jsonify, session
from agent import process_message, memory

app = Flask(__name__)
app.secret_key = __import__("os").environ.get(
    "FLASK_SECRET_KEY",
    "local-development-secret-change-before-deployment"
)

# Store conversation memory per session.
# This is suitable for a local demo, not a multi-worker production deployment.
session_memories = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")

    if not isinstance(message, str) or not message.strip():
        return jsonify({
            "success": False,
            "error": "Please enter a message."
        }), 400

    if len(message) > 2000:
        return jsonify({
            "success": False,
            "error": "Message is too long. Please keep it under 2000 characters."
        }), 400

    session_id = session.get("session_id")

    if not session_id:
        import uuid
        session_id = uuid.uuid4().hex
        session["session_id"] = session_id

    # The current agent uses a shared memory object. Save and restore
    # messages for each browser session around the request.
    current_messages = memory.get_messages()
    previous_messages = session_memories.get(session_id)

    if previous_messages is not None:
        memory.messages = previous_messages.copy()
    else:
        memory.clear()
        from agent import SYSTEM_MESSAGE
        memory.add_message({
            "role": "system",
            "content": SYSTEM_MESSAGE
        })

    try:
        reply = process_message(message)
        session_memories[session_id] = memory.get_messages().copy()

        return jsonify({
            "success": True,
            "reply": reply
        })

    except Exception:
        # Restore a usable agent state after unexpected failures.
        memory.messages = current_messages
        app.logger.exception("Unexpected chat request error")

        return jsonify({
            "success": False,
            "error": "Something went wrong. Please try again."
        }), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "application": "CampusConnect AI Support"
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
