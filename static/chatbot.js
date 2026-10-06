// =========================
// SMART-FIN AI CHATBOT
// =========================

document.addEventListener("DOMContentLoaded", () => {

    const toggleButton = document.getElementById("chatbot-toggle");
    const closeButton = document.getElementById("chatbot-close");
    const chatbotWindow = document.getElementById("chatbot-window");

    const input = document.getElementById("chatbot-input");
    const sendButton = document.getElementById("chatbot-send");

    const messages = document.getElementById("chatbot-messages");
    const quickButtons = document.querySelectorAll(".quick-btn");


    // =========================
    // OPEN CHATBOT
    // =========================

    toggleButton.addEventListener("click", () => {

        chatbotWindow.classList.toggle("active");

        if (chatbotWindow.classList.contains("active")) {
            input.focus();
        }

    });


    // =========================
    // CLOSE CHATBOT
    // =========================

    closeButton.addEventListener("click", () => {

        chatbotWindow.classList.remove("active");

    });


    // =========================
    // ADD MESSAGE
    // =========================

    function addMessage(text, sender) {

        const messageWrapper = document.createElement("div");

        messageWrapper.classList.add(
            "chat-message",
            sender === "user"
                ? "user-message"
                : "bot-message"
        );

        const bubble = document.createElement("div");

        bubble.classList.add("message-bubble");

        bubble.textContent = text;

        messageWrapper.appendChild(bubble);

        messages.appendChild(messageWrapper);

        scrollToBottom();
    }


    // =========================
    // TYPING INDICATOR
    // =========================

    function showTyping() {

        const typingWrapper = document.createElement("div");

        typingWrapper.id = "typing-indicator";

        typingWrapper.classList.add("typing-message");

        typingWrapper.innerHTML = `
            <div class="typing-bubble">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>
        `;

        messages.appendChild(typingWrapper);

        scrollToBottom();
    }


    // =========================
    // REMOVE TYPING
    // =========================

    function hideTyping() {

        const typingIndicator =
            document.getElementById("typing-indicator");

        if (typingIndicator) {
            typingIndicator.remove();
        }

    }


    // =========================
    // SCROLL
    // =========================

    function scrollToBottom() {

        messages.scrollTop = messages.scrollHeight;

    }


    // =========================
    // SEND MESSAGE
    // =========================

    async function sendMessage(customMessage = null) {

        const message =
            customMessage !== null
                ? customMessage.trim()
                : input.value.trim();


        if (!message) {
            return;
        }


        // Show user's message

        addMessage(message, "user");

        input.value = "";

        sendButton.disabled = true;

        showTyping();


        try {

            const response = await fetch("/api/chat", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    message: message
                })

            });


            const data = await response.json();


            hideTyping();


            if (!response.ok) {

                addMessage(
                    data.reply ||
                    "Sorry, something went wrong.",
                    "bot"
                );

                return;
            }


            addMessage(
                data.reply ||
                "Sorry, I couldn't generate a response.",
                "bot"
            );


        } catch (error) {

            console.error(
                "Chatbot error:",
                error
            );

            hideTyping();

            addMessage(
                "Sorry, I couldn't connect to the AI service. Please try again.",
                "bot"
            );

        } finally {

            sendButton.disabled = false;

            input.focus();

        }

    }


    // =========================
    // SEND BUTTON
    // =========================

    sendButton.addEventListener(
        "click",
        () => {
            sendMessage();
        }
    );


    // =========================
    // ENTER KEY
    // =========================

    input.addEventListener(
        "keydown",
        (event) => {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendMessage();

            }

        }
    );


    // =========================
    // QUICK BUTTONS
    // =========================

    quickButtons.forEach((button) => {

        button.addEventListener(
            "click",
            () => {

                const message =
                    button.textContent.trim();

                sendMessage(message);

            }
        );

    });

});