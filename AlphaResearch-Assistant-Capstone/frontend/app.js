const loginScreen = document.getElementById("loginScreen");
const appShell = document.getElementById("appShell");
const loginForm = document.getElementById("loginForm");
const loginId = document.getElementById("loginId");
const loginPassword = document.getElementById("loginPassword");
const loginError = document.getElementById("loginError");
const logoutButton = document.getElementById("logoutButton");
const clearChatButton = document.getElementById("clearChatButton");
const messages = document.getElementById("messages");
const chatForm = document.getElementById("chatForm");
const questionInput = document.getElementById("questionInput");
const reasoningToggle = document.getElementById("reasoningToggle");
const uploadForm = document.getElementById("uploadForm");
const fileInput = document.getElementById("fileInput");
const healthDot = document.getElementById("healthDot");
const healthText = document.getElementById("healthText");
const documentCount = document.getElementById("documentCount");
const runtimeMode = document.getElementById("runtimeMode");
const SESSION_KEY = "alpharesearch_session";
const CHAT_HISTORY_KEY = "alpharesearch_chat_history";
const CHAT_SESSION_KEY = "alpharesearch_chat_session_id";
const LAST_ANSWER_KEY = "alpharesearch_last_substantial_answer";
let conversationHistory = loadConversationHistory();
let chatSessionId = getChatSessionId();
const WELCOME_HTML = `
  <article class="message assistant welcome-message">
    <div class="avatar">AR</div>
    <div class="bubble">
      <p class="lead">Welcome to AlphaResearch Assistant.</p>
      <p>Select an SOP card or ask a direct question about SEBI rules, trading operations, settlement, commodities, derivatives, or client processes. Answers are generated from the ingested knowledge base and include retrieved source files.</p>
    </div>
  </article>
`;

function showApp() {
  loginScreen.classList.add("is-hidden");
  appShell.classList.remove("is-hidden");
  refreshStatus();
}

function showLogin() {
  appShell.classList.add("is-hidden");
  loginScreen.classList.remove("is-hidden");
  loginPassword.value = "";
  loginId.focus();
}

function isAuthenticated() {
  return Boolean(localStorage.getItem(SESSION_KEY));
}

function getChatSessionId() {
  let sessionId = localStorage.getItem(CHAT_SESSION_KEY);
  if (!sessionId) {
    sessionId = `session-${Date.now()}-${Math.random().toString(16).slice(2)}`;
    localStorage.setItem(CHAT_SESSION_KEY, sessionId);
  }
  return sessionId;
}

function loadConversationHistory() {
  try {
    return JSON.parse(localStorage.getItem(CHAT_HISTORY_KEY) || "[]");
  } catch {
    return [];
  }
}

function saveConversationHistory() {
  localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(conversationHistory.slice(-10)));
}

function isSubstantialAnswer(content) {
  const text = (content || "").trim();
  return text.length >= 120 && !(text.split(/\s+/).length < 30 && text.split("\n").length <= 2);
}

function looksLikeFollowUp(question) {
  return /\b(simplify|summari[sz]e|summary|above|previous|line|lines|word|words|short|brief|continue)\b/i.test(question);
}

loginForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const id = loginId.value.trim();
  const password = loginPassword.value.trim();

  if (!id || !password) {
    loginError.textContent = "Enter both login ID and password.";
    return;
  }

  localStorage.setItem(
    SESSION_KEY,
    JSON.stringify({
      loginId: id,
      signedInAt: new Date().toISOString(),
    })
  );
  loginError.textContent = "";
  showApp();
});

logoutButton.addEventListener("click", () => {
  localStorage.removeItem(SESSION_KEY);
  clearChat();
  showLogin();
});

clearChatButton.addEventListener("click", clearChat);

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderAssistantContent(content) {
  const cleaned = content
    .replace(/\n{3,}/g, "\n\n")
    .trim();

  const blocks = cleaned.split(/\n\s*\n/).filter(Boolean);
  return blocks
    .map((block) => {
      const lines = block.split("\n").filter(Boolean);
      const firstLine = lines[0].trim();
      const heading = firstLine.match(/^(#{1,6})\s+(.+)$/);
      const isList = lines.every((line) => /^[-*]\s+/.test(line.trim()) || /^\d+\.\s+/.test(line.trim()));

      if (isList) {
        const ordered = lines.every((line) => /^\d+\.\s+/.test(line.trim()));
        const items = lines
          .map((line) => line.replace(/^[-*]\s+/, "").replace(/^\d+\.\s+/, ""))
          .map((line) => `<li>${formatInline(line)}</li>`)
          .join("");
        return ordered ? `<ol>${items}</ol>` : `<ul>${items}</ul>`;
      }

      if (heading) {
        const level = Math.min(Math.max(heading[1].length, 2), 4);
        const rest = lines.slice(1).join("\n").trim();
        return `<h${level}>${formatInline(heading[2])}</h${level}>${rest ? renderAssistantContent(rest) : ""}`;
      }

      const numberedHeading = firstLine.match(/^(\d+(?:\.\d+)*)\s+(.+)$/);
      if (numberedHeading && lines.length > 1) {
        const rest = lines.slice(1).join("\n").trim();
        return `<section class="answer-section"><h3>${formatInline(numberedHeading[2])}</h3>${rest ? renderAssistantContent(rest) : ""}</section>`;
      }

      if (/^\d+\.\s+/.test(firstLine) && lines.length > 1) {
        const title = firstLine.replace(/^\d+\.\s+/, "");
        const children = lines.slice(1).filter((line) => /^[-*]\s+/.test(line.trim()));
        const childList = children.length
          ? `<ul>${children.map((line) => `<li>${formatInline(line.trim().replace(/^[-*]\s+/, ""))}</li>`).join("")}</ul>`
          : "";
        return `<section class="answer-section"><h3>${formatInline(title)}</h3>${childList}</section>`;
      }

      if (lines.length === 1 && lines[0].length < 80 && /:$/.test(lines[0])) {
        return `<h3>${formatInline(lines[0].replace(/:$/, ""))}</h3>`;
      }

      if (lines.length > 1 && firstLine.length < 90 && /:$/.test(firstLine)) {
        const rest = lines.slice(1).join("\n").trim();
        return `<h4>${formatInline(firstLine.replace(/:$/, ""))}</h4>${rest ? renderAssistantContent(rest) : ""}`;
      }

      return `<p>${lines.map(formatInline).join("<br>")}</p>`;
    })
    .join("");
}

function formatInline(value) {
  return value
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/\[(\d+)\]/g, '<span class="citation">[$1]</span>');
}

function addMessage(role, content, sources = [], options = {}) {
  const article = document.createElement("article");
  article.className = `message ${role}`;
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "You" : "AR";
  const bubble = document.createElement("div");
  bubble.className = "bubble";

  if (role === "assistant") {
    bubble.innerHTML = renderAssistantContent(escapeHtml(content));
  } else {
    bubble.textContent = content;
  }

  if (sources.length) {
    const sourceBlock = document.createElement("div");
    sourceBlock.className = "sources";
    sources.forEach((source) => {
      const chip = document.createElement("span");
      chip.textContent = source;
      sourceBlock.appendChild(chip);
    });
    bubble.appendChild(sourceBlock);
  }

  if (role === "assistant" && options.rateable) {
    bubble.appendChild(createRatingControl(options.question || "", content));
  }

  article.append(avatar, bubble);
  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;
  updateClearChatState();
  return article;
}

function updateClearChatState() {
  const nonWelcomeMessages = messages.querySelectorAll(".message:not(.welcome-message)");
  clearChatButton.disabled = nonWelcomeMessages.length === 0;
}

function clearChat() {
  messages.innerHTML = WELCOME_HTML;
  questionInput.value = "";
  conversationHistory = [];
  localStorage.removeItem(CHAT_HISTORY_KEY);
  localStorage.removeItem(CHAT_SESSION_KEY);
  localStorage.removeItem(LAST_ANSWER_KEY);
  chatSessionId = getChatSessionId();
  updateClearChatState();
}

function createRatingControl(question, answer) {
  const wrapper = document.createElement("div");
  wrapper.className = "rating";

  const label = document.createElement("span");
  label.textContent = "Rate response";
  wrapper.appendChild(label);

  const stars = document.createElement("div");
  stars.className = "stars";
  wrapper.appendChild(stars);

  const note = document.createElement("p");
  note.className = "rating-note";
  note.textContent = "Your rating helps AlphaResearch improve answer quality.";
  wrapper.appendChild(note);

  const ratingId = `rating-${Date.now()}-${Math.random().toString(16).slice(2)}`;

  function paintStars(value) {
    stars.querySelectorAll("button").forEach((star, starIndex) => {
      star.classList.toggle("active", starIndex < value);
    });
  }

  for (let index = 1; index <= 5; index += 1) {
    const button = document.createElement("button");
    button.type = "button";
    button.setAttribute("aria-label", `${index} star rating`);
    button.textContent = "★";
    button.addEventListener("mouseenter", () => paintStars(index));
    button.addEventListener("focus", () => paintStars(index));
    button.addEventListener("click", () => {
      paintStars(index);
      localStorage.setItem(
        ratingId,
        JSON.stringify({
          rating: index,
          question,
          answerPreview: answer.slice(0, 240),
          createdAt: new Date().toISOString(),
        })
      );
      wrapper.dataset.rating = String(index);
      label.textContent = `Rated ${index}/5`;
      note.textContent =
        index >= 4
          ? "Thank you. I will reinforce this response style for future answers."
          : "Thank you. I will use this feedback to make future answers clearer and more useful.";
    });
    stars.appendChild(button);
  }

  stars.addEventListener("mouseleave", () => {
    paintStars(Number(wrapper.dataset.rating || 0));
  });

  return wrapper;
}

async function refreshStatus() {
  try {
    const [health, stats] = await Promise.all([
      fetch("/health").then((res) => res.json()),
      fetch("/api/stats").then((res) => res.json()).catch(() => null),
    ]);
    healthDot.className = "dot good";
    healthText.textContent = health.status || "Healthy";
    if (stats?.system) {
      documentCount.textContent = stats.system.documents_in_kb;
      runtimeMode.textContent = stats.system.llm_model;
    }
  } catch (error) {
    healthDot.className = "dot bad";
    healthText.textContent = "API unavailable";
  }
}

async function ask(question, displayText = question) {
  addMessage("user", displayText);
  if (conversationHistory.length === 0) {
    conversationHistory = extractVisibleConversation();
  }
  if (looksLikeFollowUp(question) && !conversationHistory.some((turn) => turn.role === "assistant" && isSubstantialAnswer(turn.content))) {
    const lastAnswer = localStorage.getItem(LAST_ANSWER_KEY);
    if (lastAnswer) {
      conversationHistory.push({ role: "assistant", content: lastAnswer });
    }
  }
  const historyForRequest = conversationHistory.slice(-8);
  conversationHistory.push({ role: "user", content: displayText });
  const loading = addMessage("assistant", "Analyzing knowledge base and retrieved controls...");

  try {
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        session_id: chatSessionId,
        conversation_history: historyForRequest,
        enable_reasoning: reasoningToggle.checked,
        top_k: reasoningToggle.checked ? 6 : 3,
      }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Request failed");
    }

    loading.remove();
    const summary = data.retrieval_summary
      ? `\n\nConfidence ${Math.round((data.confidence || 0) * 100)} percent. Response time ${Math.round(data.execution_time_ms)} ms.`
      : "";
    addMessage(
      "assistant",
      `${data.answer || "No answer generated."}${summary}`,
      data.sources || [],
      { rateable: true, question: displayText }
    );
    conversationHistory.push({
      role: "assistant",
      content: data.answer || "No answer generated.",
    });
    if (isSubstantialAnswer(data.answer || "")) {
      localStorage.setItem(LAST_ANSWER_KEY, data.answer);
    }
    conversationHistory = conversationHistory.slice(-10);
    refreshStatus();
  } catch (error) {
    loading.remove();
    addMessage("assistant", `I could not complete the request. ${error.message}`);
    conversationHistory.push({
      role: "assistant",
      content: `I could not complete the request. ${error.message}`,
    });
  }
  saveConversationHistory();
}

function extractVisibleConversation() {
  return Array.from(messages.querySelectorAll(".message:not(.welcome-message)"))
    .map((message) => {
      const role = message.classList.contains("user") ? "user" : "assistant";
      const bubble = message.querySelector(".bubble");
      return {
        role,
        content: (bubble?.innerText || "").replace(/Rate response[\s\S]*$/, "").trim(),
      };
    })
    .filter((turn) => turn.content);
}

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) return;
  questionInput.value = "";
  ask(question);
});

questionInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    chatForm.requestSubmit();
  }
});

document.querySelectorAll("[data-question]").forEach((button) => {
  button.addEventListener("click", () => {
    const question = button.dataset.question;
    const displayText = button.dataset.display || question;
    ask(question, displayText);
  });
});

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = fileInput.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);
  const loading = addMessage("assistant", `Uploading and indexing ${file.name}...`);

  try {
    const response = await fetch("/api/documents/upload", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Upload failed");
    }
    loading.remove();
    addMessage("assistant", `${file.name} has been indexed successfully. Created ${data.chunks_created} retrieval chunks.`);
    fileInput.value = "";
    refreshStatus();
  } catch (error) {
    loading.remove();
    addMessage("assistant", `Upload could not be indexed. ${error.message}`);
  }
});

if (isAuthenticated()) {
  showApp();
} else {
  showLogin();
}

updateClearChatState();
