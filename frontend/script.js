/**
 * College Chatbot Frontend Script
 * Handles UI interactions and API communication.
 */

// ===== Configuration =====
const API_BASE = "http://localhost:5000";
// Uses Python FastAPI directly — no proxy needed

// ===== DOM Elements =====
const chatMessages = document.getElementById("chatMessages");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const clearChat = document.getElementById("clearChat");
const menuToggle = document.getElementById("menuToggle");
const sidebar = document.querySelector(".sidebar");
const statusDot = document.querySelector(".status-dot");
const statusText = document.getElementById("statusText");
const quickBtns = document.querySelectorAll(".quick-btn");

// ===== State =====
let isProcessing = false;
let messageHistory = [];

// ===== Initialize =====
document.addEventListener("DOMContentLoaded", () => {
  checkApiHealth();
  setupEventListeners();
  loadChatHistory();
  autoResizeTextarea();
});

// ===== Event Listeners =====
function setupEventListeners() {
  // Send button
  sendBtn.addEventListener("click", sendMessage);

  // Enter to send, Shift+Enter for new line
  userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // Enable/disable send button based on input
  userInput.addEventListener("input", () => {
    sendBtn.disabled = userInput.value.trim() === "" || isProcessing;
    autoResizeTextarea();
  });

  // Clear chat
  clearChat.addEventListener("click", clearChatHistory);

  // Mobile menu toggle
  menuToggle.addEventListener("click", toggleSidebar);

  // Quick question buttons
  quickBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const question = btn.getAttribute("data-question");
      userInput.value = question;
      sendBtn.disabled = false;
      sendMessage();
      closeSidebar();
    });
  });

  // Close sidebar on overlay click
  document.addEventListener("click", (e) => {
    if (
      sidebar.classList.contains("open") &&
      !sidebar.contains(e.target) &&
      e.target !== menuToggle
    ) {
      closeSidebar();
    }
  });
}

// ===== Auto-resize textarea =====
function autoResizeTextarea() {
  userInput.style.height = "auto";
  userInput.style.height = Math.min(userInput.scrollHeight, 120) + "px";
}

// ===== API Health Check =====
async function checkApiHealth() {
  try {
    const response = await fetch(API_BASE + "/health", { 
      method: "GET",
      signal: AbortSignal.timeout(5000)
    });
    const data = await response.json();

    if (data.status === "healthy" && data.faiss_index) {
      setStatus("online", `Online • ${data.total_vectors} vectors loaded`);
    } else {
      setStatus("online", "Online (Vector DB not loaded yet)");
    }
  } catch (error) {
    setStatus("offline", "Backend offline — start the Python API first");
    console.error("Health check failed:", error);
  }
}

function setStatus(state, text) {
  statusDot.className = "status-dot " + state;
  statusText.textContent = text;
}

// ===== Send Message =====
async function sendMessage() {
  const question = userInput.value.trim();
  if (!question || isProcessing) return;

  isProcessing = true;
  sendBtn.disabled = true;
  userInput.value = "";
  autoResizeTextarea();

  // Add user message
  addMessage("user", question);

  // Show typing indicator
  const typingEl = showTypingIndicator();

  try {
    const response = await fetch(API_BASE + "/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question, top_k: 5 }),
    });

    // Remove typing indicator
    typingEl.remove();

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Server error (${response.status})`);
    }

    const data = await response.json();

    // Add bot response
    addMessage("bot", data.answer, data.sources);
  } catch (error) {
    typingEl.remove();
    console.error("Chat error:", error);

    let errorMsg =
      "Sorry, I encountered an error. Please make sure the backend server is running.";
    if (error.message.includes("Failed to fetch") || error.message.includes("NetworkError")) {
      errorMsg =
        "Cannot connect to the server. Please ensure both the Python API and Node.js server are running.";
    } else if (error.message) {
      errorMsg = `Error: ${error.message}`;
    }

    addMessage("bot", errorMsg, [], true);
  }

  isProcessing = false;
  sendBtn.disabled = userInput.value.trim() === "";
}

// ===== Add Message to Chat =====
function addMessage(role, text, sources = [], isError = false) {
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${role}-message`;

  const time = new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  // Format message text (convert markdown-like formatting)
  let formattedText = formatText(text);

  // Build sources HTML
  let sourcesHTML = "";
  if (sources && sources.length > 0) {
    sourcesHTML = `
      <div class="sources">
        <strong>📎 Sources:</strong>
        ${sources.map((s) => `<a href="${s}" target="_blank">${s}</a>`).join("")}
      </div>
    `;
  }

  if (role === "user") {
    messageDiv.innerHTML = `
      <div class="message-avatar">👤</div>
      <div class="message-content">
        <div class="message-bubble">${formattedText}</div>
        <span class="message-time">${time}</span>
      </div>
    `;
  } else {
    messageDiv.innerHTML = `
      <div class="message-avatar">🎓</div>
      <div class="message-content">
        <div class="message-bubble ${isError ? "error-bubble" : ""}">${formattedText}${sourcesHTML}</div>
        <span class="message-time">${time}</span>
      </div>
    `;
  }

  chatMessages.appendChild(messageDiv);
  scrollToBottom();

  // Save to history
  messageHistory.push({ role, text, time });
  saveChatHistory();
}

// ===== Format text (basic markdown) =====
function formatText(text) {
  // Escape HTML
  text = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // Bold **text**
  text = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

  // Italic *text*
  text = text.replace(/\*(.*?)\*/g, "<em>$1</em>");

  // Bullet points
  text = text.replace(/^[\s]*[-•]\s+(.*)/gm, "<li>$1</li>");
  text = text.replace(/(<li>.*<\/li>)/gs, "<ul>$1</ul>");
  // Clean up nested ul
  text = text.replace(/<\/ul>\s*<ul>/g, "");

  // Numbered lists
  text = text.replace(/^[\s]*\d+\.\s+(.*)/gm, "<li>$1</li>");

  // Line breaks
  text = text.replace(/\n/g, "<br>");

  // Clean up
  text = text.replace(/<br><ul>/g, "<ul>");
  text = text.replace(/<\/ul><br>/g, "</ul>");

  return text;
}

// ===== Typing Indicator =====
function showTypingIndicator() {
  const typingDiv = document.createElement("div");
  typingDiv.className = "message bot-message";
  typingDiv.id = "typingIndicator";
  typingDiv.innerHTML = `
    <div class="message-avatar">🎓</div>
    <div class="message-content">
      <div class="message-bubble">
        <div class="typing-indicator">
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
      </div>
    </div>
  `;
  chatMessages.appendChild(typingDiv);
  scrollToBottom();
  return typingDiv;
}

// ===== Scroll to Bottom =====
function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ===== Sidebar Toggle =====
function toggleSidebar() {
  sidebar.classList.toggle("open");
}

function closeSidebar() {
  sidebar.classList.remove("open");
}

// ===== Chat History =====
function saveChatHistory() {
  try {
    // Keep last 50 messages
    const toSave = messageHistory.slice(-50);
    localStorage.setItem("bvrit_chat_history", JSON.stringify(toSave));
  } catch (e) {
    console.warn("Could not save chat history:", e);
  }
}

function loadChatHistory() {
  try {
    const saved = localStorage.getItem("bvrit_chat_history");
    if (saved) {
      const history = JSON.parse(saved);
      history.forEach((msg) => {
        const messageDiv = document.createElement("div");
        messageDiv.className = `message ${msg.role}-message`;

        const formattedText = formatText(msg.text);

        if (msg.role === "user") {
          messageDiv.innerHTML = `
            <div class="message-avatar">👤</div>
            <div class="message-content">
              <div class="message-bubble">${formattedText}</div>
              <span class="message-time">${msg.time}</span>
            </div>
          `;
        } else {
          messageDiv.innerHTML = `
            <div class="message-avatar">🎓</div>
            <div class="message-content">
              <div class="message-bubble">${formattedText}</div>
              <span class="message-time">${msg.time}</span>
            </div>
          `;
        }

        chatMessages.appendChild(messageDiv);
      });
      messageHistory = history;
      scrollToBottom();
    }
  } catch (e) {
    console.warn("Could not load chat history:", e);
  }
}

function clearChatHistory() {
  // Keep the welcome message
  const welcome = chatMessages.querySelector(".welcome-message");
  chatMessages.innerHTML = "";
  if (welcome) chatMessages.appendChild(welcome);
  messageHistory = [];
  localStorage.removeItem("bvrit_chat_history");
}

// Periodic health check
setInterval(checkApiHealth, 30000);
