// ====================================
// AI STUDY BUDDY - SCRIPT.JS
// ====================================

const chatContainer = document.getElementById("chatContainer");
const userInput = document.getElementById("userInput");
const typingIndicator = document.getElementById("typingIndicator");
const welcomeSection = document.getElementById("welcomeSection");

const fileInput = document.getElementById("fileInput");
const imageInput = document.getElementById("imageInput");
const selectedFile = document.getElementById("selectedFile");

// ====================================
// AUTO RESIZE TEXTAREA
// ====================================

userInput.addEventListener("input", () => {
    userInput.style.height = "auto";
    userInput.style.height = userInput.scrollHeight + "px";
});

// ====================================
// ENTER TO SEND
// ====================================

userInput.addEventListener("keydown", (event) => {

    if (event.key === "Enter" && !event.shiftKey) {

        event.preventDefault();

        sendMessage();
    }

});

// ====================================
// FILE PREVIEW
// ====================================

if (fileInput) {

    fileInput.addEventListener("change", function () {

        if (this.files.length > 0) {

            selectedFile.innerHTML =
                "Document Selected: " +
                this.files[0].name;

        }

    });

}

if (imageInput) {

    imageInput.addEventListener("change", function () {

        if (this.files.length > 0) {

            selectedFile.innerHTML =
                "Image Selected: " +
                this.files[0].name;

        }

    });

}

// ====================================
// NEW CHAT
// ====================================

function newChat() {

    chatContainer.innerHTML = "";

    welcomeSection.style.display = "block";

    userInput.value = "";

    if(selectedFile){
        selectedFile.innerHTML = "";
    }

}

// ====================================
// QUICK ACTIONS
// ====================================

function fillPrompt(text) {

    userInput.value = text;

    userInput.focus();

}

// ====================================
// ADD MESSAGE
// ====================================

function addMessage(message, sender) {

    const messageDiv =
        document.createElement("div");

    messageDiv.classList.add("message");

    if (sender === "user") {

        messageDiv.classList.add(
            "user-message"
        );

    } else {

        messageDiv.classList.add(
            "bot-message"
        );

    }

    messageDiv.innerHTML =
        formatResponse(message);

    chatContainer.appendChild(
        messageDiv
    );

    scrollToBottom();

}

// ====================================
// FORMAT RESPONSE
// ====================================

function formatResponse(text) {

    return text.replace(
        /\n/g,
        "<br>"
    );

}

// ====================================
// SCROLL
// ====================================

function scrollToBottom() {

    chatContainer.scrollTop =
        chatContainer.scrollHeight;

}

// ====================================
// TYPING
// ====================================

function showTyping() {

    typingIndicator.style.display =
        "block";

}

function hideTyping() {

    typingIndicator.style.display =
        "none";

}

// ====================================
// SEND MESSAGE
// ====================================

async function sendMessage() {

    const message =
        userInput.value.trim();

    if (
        message === "" &&
        !fileInput.files[0] &&
        !imageInput.files[0]
    ) {
        return;
    }

    welcomeSection.style.display =
        "none";

    if (message) {

        addMessage(
            message,
            "user"
        );

    }

    showTyping();

    const formData =
        new FormData();

    formData.append(
        "message",
        message
    );

    if (fileInput.files[0]) {

        formData.append(
            "document",
            fileInput.files[0]
        );

    }

    if (imageInput.files[0]) {

        formData.append(
            "image",
            imageInput.files[0]
        );

    }

    try {

        const response =
            await fetch(
                "/chat",
                {
                    method: "POST",
                    body: formData
                }
            );

        const data =
            await response.json();

        hideTyping();

        typeResponse(
            data.response
        );

        saveChatHistory(
            message
        );

        userInput.value = "";

        userInput.style.height =
            "50px";

        fileInput.value = "";

        imageInput.value = "";

        if (selectedFile) {

            selectedFile.innerHTML =
                "";

        }

    }
    catch (error) {

        hideTyping();

        addMessage(
            "Unable to connect to server.",
            "bot"
        );

        console.error(error);

    }

}

// ====================================
// TYPE RESPONSE
// ====================================

function typeResponse(text) {

    const botDiv =
        document.createElement("div");

    botDiv.classList.add(
        "message"
    );

    botDiv.classList.add(
        "bot-message"
    );

    chatContainer.appendChild(
        botDiv
    );

    let index = 0;

    const speed = 10;

    const timer =
        setInterval(() => {

            if (
                index < text.length
            ) {

                botDiv.innerHTML =
                    formatResponse(
                        text.substring(
                            0,
                            index + 1
                        )
                    );

                index++;

                scrollToBottom();

            }
            else {

                clearInterval(
                    timer
                );

            }

        }, speed);

}

// ====================================
// CHAT HISTORY
// ====================================

function saveChatHistory(message) {

    let history =
        JSON.parse(
            localStorage.getItem(
                "studyBuddyHistory"
            )
        ) || [];

    history.unshift(
        message
    );

    history =
        history.slice(
            0,
            15
        );

    localStorage.setItem(
        "studyBuddyHistory",
        JSON.stringify(history)
    );

    loadHistory();

}

// ====================================
// LOAD HISTORY
// ====================================

function loadHistory() {

    const historyContainer =
        document.getElementById(
            "chatHistory"
        );

    if (!historyContainer)
        return;

    let history =
        JSON.parse(
            localStorage.getItem(
                "studyBuddyHistory"
            )
        ) || [];

    historyContainer.innerHTML =
        "";

    history.forEach(chat => {

        const item =
            document.createElement(
                "div"
            );

        item.classList.add(
            "history-item"
        );

        item.textContent =
            chat;

        item.onclick =
            () => {

                userInput.value =
                    chat;

            };

        historyContainer.appendChild(
            item
        );

    });

}

// ====================================
// VOICE INPUT
// ====================================

function startVoiceInput() {

    if (
        !(
            'webkitSpeechRecognition'
            in window
        )
    ) {

        alert(
            "Voice input not supported."
        );

        return;

    }

    const recognition =
        new webkitSpeechRecognition();

    recognition.lang =
        "en-US";

    recognition.start();

    recognition.onresult =
        function(event) {

            userInput.value =
                event.results[0][0]
                .transcript;

        };

}

// ====================================
// EXPORT CHATS
// ====================================

function exportChats() {

    const history =
        localStorage.getItem(
            "studyBuddyHistory"
        );

    const blob =
        new Blob(
            [history],
            {
                type:
                "application/json"
            }
        );

    const link =
        document.createElement(
            "a"
        );

    link.href =
        URL.createObjectURL(
            blob
        );

    link.download =
        "study_buddy_history.json";

    link.click();

}

// ====================================
// THEME
// ====================================

function toggleTheme() {

    document.body.classList.toggle(
        "light-theme"
    );

}

// ====================================
// PAGE LOAD
// ====================================

window.onload = function () {

    loadHistory();

};