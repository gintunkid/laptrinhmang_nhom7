const socket = io();

const chatBox = document.getElementById("chat-box");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");

// Thêm tin nhắn vào giao diện
function addMessage(message, sender) {
    const messageElement = document.createElement("div");
    messageElement.classList.add("message", sender);
    messageElement.innerText = message;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Gửi tin nhắn khi nhấn Enter
messageInput.addEventListener("keydown", function(event) {
    if (event.key === "Enter" && messageInput.value.trim() !== "") {
        const message = messageInput.value.trim();
        addMessage(message, "user");
        socket.emit("send_message", { message });
        messageInput.value = "";
    }
});

// Nhận phản hồi từ server
socket.on("receive_message", (data) => {
    addMessage(data.message, "bot");
});
