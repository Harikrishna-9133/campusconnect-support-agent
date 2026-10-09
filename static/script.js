
const form = document.getElementById("chat-form");
const input = document.getElementById("message-input");
const messages = document.getElementById("messages");
const sendButton = document.getElementById("send-button");


function addMessage(text, role) {
    const messageElement = document.createElement("div");
    messageElement.classList.add("message", role);

    const contentElement = document.createElement("div");
    contentElement.classList.add("message-content");

    if (role !== "assistant") {
        contentElement.textContent = text;
    } else {
        // Safely render a useful subset of Markdown.
        const lines = String(text).split("\n");
        let listElement = null;
        let listType = null;

        function closeList() {
            listElement = null;
            listType = null;
        }

        function formatInline(value, parent) {
            // Split text around bold, inline-code, and italic markers.
            const pattern = /(\*\*[^*]+\*\*|`[^`]+`|\*[^*\n]+\*)/g;
            let lastIndex = 0;
            let match;

            while ((match = pattern.exec(value)) !== null) {
                parent.appendChild(
                    document.createTextNode(value.slice(lastIndex, match.index))
                );

                const token = match[0];
                const element = document.createElement(
                    token.startsWith("**") ? "strong" :
                        token.startsWith("`") ? "code" : "em"
                );

                element.textContent =
                    token.startsWith("**") ? token.slice(2, -2) :
                        token.startsWith("`") ? token.slice(1, -1) :
                            token.slice(1, -1);

                parent.appendChild(element);
                lastIndex = pattern.lastIndex;
            }

            parent.appendChild(
                document.createTextNode(value.slice(lastIndex))
            );
        }

        for (const rawLine of lines) {
            const line = rawLine.trim();

            if (!line) {
                closeList();
                continue;
            }

            const headingMatch = line.match(/^#{1,3}\s+(.+)$/);
            const bulletMatch = line.match(/^[-*]\s+(.+)$/);
            const numberMatch = line.match(/^\d+[.)]\s+(.+)$/);

            if (headingMatch) {
                closeList();
                const heading = document.createElement("h4");
                formatInline(headingMatch[1], heading);
                contentElement.appendChild(heading);
            } else if (bulletMatch || numberMatch) {
                const nextType = bulletMatch ? "ul" : "ol";

                if (listType !== nextType || !listElement) {
                    closeList();
                    listType = nextType;
                    listElement = document.createElement(nextType);
                    contentElement.appendChild(listElement);
                }

                const item = document.createElement("li");
                formatInline(
                    bulletMatch ? bulletMatch[1] : numberMatch[1],
                    item
                );
                listElement.appendChild(item);
            } else {
                closeList();
                const paragraph = document.createElement("p");
                formatInline(line, paragraph);
                contentElement.appendChild(paragraph);
            }
        }
    }

    messageElement.appendChild(contentElement);
    messages.appendChild(messageElement);
    messages.scrollTop = messages.scrollHeight;
}


async function sendMessage(message) {
    addMessage(message, "user");

    const typing = document.createElement("div");
    typing.className = "typing";
    typing.textContent = "CampusConnect is checking your request...";
    messages.appendChild(typing);

    sendButton.disabled = true;
    input.disabled = true;

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message })
        });

        const data = await response.json();
        typing.remove();

        if (!response.ok || !data.success) {
            addMessage(
                data.error || "Sorry, something went wrong. Please try again.",
                "assistant"
            );
        } else {
            addMessage(data.reply, "assistant");
        }
    } catch (error) {
        typing.remove();
        addMessage(
            "I couldn't reach the support server. Please check that it is running and try again.",
            "assistant"
        );
    } finally {
        sendButton.disabled = false;
        input.disabled = false;
        input.focus();
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const message = input.value.trim();

    if (!message || sendButton.disabled) {
        return;
    }

    input.value = "";
    await sendMessage(message);
});

document.querySelectorAll(".suggestion").forEach((button) => {
    button.addEventListener("click", async () => {
        if (sendButton.disabled) return;
        await sendMessage(button.dataset.message);
    });
});
