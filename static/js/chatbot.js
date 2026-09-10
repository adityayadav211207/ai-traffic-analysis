/**
 * TrafficVision AI - ChatGPT-Style Conversational Engine
 */

document.addEventListener("DOMContentLoaded", () => {
    initChatApp();
});

function initChatApp() {
    const chatInput = document.getElementById("chatTextarea");
    const sendBtn = document.getElementById("sendChatBtn");
    const messagesContainer = document.getElementById("chatMessagesInner");
    const scrollContainer = document.getElementById("chatMessagesContainer");
    const toggleSidebarBtn = document.getElementById("toggleSidebarBtn");
    const chatSidebar = document.getElementById("chatSidebar");
    const newChatBtn = document.getElementById("newChatBtn");
    const clearChatBtn = document.getElementById("clearChatBtn");
    const exportChatBtn = document.getElementById("exportChatBtn");
    const voiceBtn = document.getElementById("voiceInputBtn");
    const sessionsListEl = document.getElementById("chatSessionsList");

    let currentSessionId = Date.now().toString();
    let isGenerating = false;

    // --------------------------------------------------------------------------
    // 1. AUTO-RESIZING TEXTAREA & SEND HANDLING
    // --------------------------------------------------------------------------
    if (chatInput) {
        chatInput.addEventListener("input", () => {
            chatInput.style.height = "auto";
            chatInput.style.height = Math.min(chatInput.scrollHeight, 140) + "px";
            if (sendBtn) {
                sendBtn.disabled = chatInput.value.trim().length === 0;
            }
        });

        chatInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                submitUserQuery();
            }
        });
    }

    if (sendBtn) {
        sendBtn.addEventListener("click", () => {
            submitUserQuery();
        });
    }

    // --------------------------------------------------------------------------
    // 2. SIDEBAR TOGGLE & SHORTCUT (Ctrl/Cmd + S)
    // --------------------------------------------------------------------------
    if (toggleSidebarBtn && chatSidebar) {
        toggleSidebarBtn.addEventListener("click", () => {
            chatSidebar.classList.toggle("collapsed");
        });
    }

    document.addEventListener("keydown", (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === "s") {
            e.preventDefault();
            if (chatSidebar) chatSidebar.classList.toggle("collapsed");
        }
    });

    // --------------------------------------------------------------------------
    // 3. NEW CHAT & RESET VIEW
    // --------------------------------------------------------------------------
    if (newChatBtn) {
        newChatBtn.addEventListener("click", () => {
            startNewSession();
        });
    }

    if (clearChatBtn) {
        clearChatBtn.addEventListener("click", () => {
            if (confirm("Are you sure you want to clear this conversation?")) {
                deleteCurrentSession();
            }
        });
    }

    if (exportChatBtn) {
        exportChatBtn.addEventListener("click", () => {
            exportCurrentConversation();
        });
    }

    // --------------------------------------------------------------------------
    // 4. SPEECH-TO-TEXT (VOICE RECOGNITION)
    // --------------------------------------------------------------------------
    if (voiceBtn && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "en-US";

        let isListening = false;

        voiceBtn.addEventListener("click", () => {
            if (!isListening) {
                try {
                    recognition.start();
                    isListening = true;
                    voiceBtn.classList.add("listening");
                    voiceBtn.title = "Listening... Speak now";
                } catch (err) {
                    console.error("Speech recognition start error:", err);
                }
            } else {
                recognition.stop();
                isListening = false;
                voiceBtn.classList.remove("listening");
            }
        });

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            if (chatInput) {
                chatInput.value = transcript;
                chatInput.style.height = "auto";
                chatInput.style.height = Math.min(chatInput.scrollHeight, 140) + "px";
                if (sendBtn) sendBtn.disabled = false;
                chatInput.focus();
            }
        };

        recognition.onerror = (e) => {
            console.error("Speech error", e);
            isListening = false;
            voiceBtn.classList.remove("listening");
        };

        recognition.onend = () => {
            isListening = false;
            voiceBtn.classList.remove("listening");
        };
    } else if (voiceBtn) {
        voiceBtn.style.display = "none";
    }

    // --------------------------------------------------------------------------
    // 5. CHAT SUBMISSION LOGIC
    // --------------------------------------------------------------------------
    function submitUserQuery() {
        if (!chatInput) return;
        const text = chatInput.value.trim();
        if (!text || isGenerating) return;

        // Hide Welcome Hero if visible
        const welcomeHero = document.getElementById("chatWelcomeHero");
        if (welcomeHero) welcomeHero.style.display = "none";

        // Append User Message
        appendMessage("user", text);

        // Reset input
        chatInput.value = "";
        chatInput.style.height = "auto";
        if (sendBtn) sendBtn.disabled = true;

        // Save session title if first prompt
        updateSessionTitle(currentSessionId, text);

        // Show Typing Indicator
        isGenerating = true;
        const typingEl = showTypingIndicator();

        // Scroll
        scrollToBottom();

        // Send API Request
        fetch("/api/ai-chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text })
        })
        .then(res => res.json())
        .then(data => {
            typingEl.remove();
            isGenerating = false;
            const aiResponse = data.response || "Neural engine could not process the query.";
            appendMessage("ai", aiResponse);
            saveCurrentSession();
            scrollToBottom();
        })
        .catch(err => {
            console.error(err);
            typingEl.remove();
            isGenerating = false;
            appendMessage("ai", "⚠️ **Connection Error**: Unable to reach TrafficVision neural engine. Please check system telemetry.");
            scrollToBottom();
        });
    }

    // --------------------------------------------------------------------------
    // 6. MESSAGE RENDERING & MARKDOWN PARSING
    // --------------------------------------------------------------------------
    function formatMarkdown(text) {
        let formatted = text
            // Code blocks
            .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
            // Inline code
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            // Bold
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Italic
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Blockquotes
            .replace(/^>\s*(.*?)$/gm, '<blockquote>$1</blockquote>')
            // Bullet points
            .replace(/^\s*•\s*(.*?)$/gm, '<li>$1</li>')
            .replace(/^\s*\*\s*(.*?)$/gm, '<li>$1</li>')
            .replace(/^\s*-\s*(.*?)$/gm, '<li>$1</li>')
            // Line breaks
            .replace(/\n\n/g, '<br><br>')
            .replace(/\n/g, '<br>');

        // Wrap list items
        if (formatted.includes('<li>')) {
            formatted = formatted.replace(/(<li>.*?<\/li>)/gs, '<ul>$1</ul>');
        }

        return formatted;
    }

    function appendMessage(role, text) {
        if (!messagesContainer) return;

        const row = document.createElement("div");
        row.className = `chat-message-row ${role === 'user' ? 'user-row' : 'ai-row'}`;

        if (role === 'user') {
            row.innerHTML = `
                <div class="message-content-wrapper">
                    <span class="message-sender-name">You</span>
                    <div class="message-bubble user-bubble">${escapeHtml(text)}</div>
                </div>
                <div class="message-avatar user-avatar">
                    <i class="fa-solid fa-user-astronaut"></i>
                </div>
            `;
        } else {
            const parsedHtml = formatMarkdown(text);
            const msgId = "msg_" + Date.now() + "_" + Math.floor(Math.random()*1000);

            row.innerHTML = `
                <div class="message-avatar ai-avatar">
                    <i class="fa-solid fa-robot"></i>
                </div>
                <div class="message-content-wrapper">
                    <span class="message-sender-name">TrafficVision AI</span>
                    <div class="message-bubble ai-bubble" id="${msgId}">${parsedHtml}</div>
                    <div class="message-actions-toolbar">
                        <button type="button" class="msg-action-btn copy-btn" title="Copy response" onclick="copyMessageText('${msgId}')">
                            <i class="fa-regular fa-copy"></i>
                            <span>Copy</span>
                        </button>
                        <button type="button" class="msg-action-btn speak-btn" title="Read aloud" onclick="speakMessageText('${msgId}')">
                            <i class="fa-solid fa-volume-high"></i>
                        </button>
                        <button type="button" class="msg-action-btn vote-up" title="Helpful" onclick="voteMessage(this, 'up')">
                            <i class="fa-regular fa-thumbs-up"></i>
                        </button>
                        <button type="button" class="msg-action-btn vote-down" title="Not helpful" onclick="voteMessage(this, 'down')">
                            <i class="fa-regular fa-thumbs-down"></i>
                        </button>
                    </div>
                </div>
            `;
        }

        messagesContainer.appendChild(row);
    }

    function showTypingIndicator() {
        const row = document.createElement("div");
        row.className = "chat-message-row ai-row typing-row";
        row.innerHTML = `
            <div class="message-avatar ai-avatar">
                <i class="fa-solid fa-robot"></i>
            </div>
            <div class="message-content-wrapper">
                <span class="message-sender-name">TrafficVision AI</span>
                <div class="typing-dots">
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                </div>
                <span class="typing-label">Analyzing traffic telemetry & neural vectors...</span>
            </div>
        `;
        messagesContainer.appendChild(row);
        return row;
    }

    function scrollToBottom() {
        if (scrollContainer) {
            scrollContainer.scrollTop = scrollContainer.scrollHeight;
        }
    }

    function escapeHtml(string) {
        return String(string)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // --------------------------------------------------------------------------
    // 7. SESSION SESSIONS MANAGEMENT (localStorage)
    // --------------------------------------------------------------------------
    function getSessions() {
        try {
            return JSON.parse(localStorage.getItem("tv_ai_sessions") || "{}");
        } catch {
            return {};
        }
    }

    function saveSessions(sessions) {
        try {
            localStorage.setItem("tv_ai_sessions", JSON.stringify(sessions));
        } catch (e) {
            console.error("Storage error:", e);
        }
    }

    function renderSessionsList() {
        if (!sessionsListEl) return;
        const sessions = getSessions();
        const keys = Object.keys(sessions).reverse();

        sessionsListEl.innerHTML = "";

        if (keys.length === 0) {
            sessionsListEl.innerHTML = `
                <div style="padding: 10px; font-size: 0.78rem; color: #64748B; text-align: center;">
                    No past sessions yet.
                </div>
            `;
            return;
        }

        keys.forEach(id => {
            const s = sessions[id];
            const item = document.createElement("div");
            item.className = `chat-session-item ${id === currentSessionId ? 'active' : ''}`;
            item.innerHTML = `
                <i class="fa-regular fa-message session-icon"></i>
                <span class="session-title">${escapeHtml(s.title || 'Analysis Session')}</span>
                <button type="button" class="session-delete-btn" title="Delete Session" onclick="deleteSessionById('${id}', event)">
                    <i class="fa-solid fa-trash-can"></i>
                </button>
            `;
            item.addEventListener("click", () => {
                loadSession(id);
            });
            sessionsListEl.appendChild(item);
        });
    }

    function updateSessionTitle(id, firstPrompt) {
        const sessions = getSessions();
        if (!sessions[id]) {
            sessions[id] = {
                title: firstPrompt.length > 28 ? firstPrompt.substring(0, 28) + "..." : firstPrompt,
                messages: []
            };
        }
        saveSessions(sessions);
        renderSessionsList();
    }

    function saveCurrentSession() {
        if (!messagesContainer) return;
        const rows = messagesContainer.querySelectorAll(".chat-message-row:not(.typing-row)");
        const messageList = [];

        rows.forEach(r => {
            const isUser = r.classList.contains("user-row");
            const bubble = r.querySelector(".message-bubble");
            if (bubble) {
                messageList.push({
                    role: isUser ? "user" : "ai",
                    text: isUser ? bubble.innerText : bubble.innerHTML,
                    isHtml: !isUser
                });
            }
        });

        const sessions = getSessions();
        if (!sessions[currentSessionId]) {
            sessions[currentSessionId] = { title: "Traffic Analysis Session", messages: [] };
        }
        sessions[currentSessionId].messages = messageList;
        saveSessions(sessions);
    }

    function loadSession(id) {
        const sessions = getSessions();
        const s = sessions[id];
        if (!s) return;

        currentSessionId = id;
        renderSessionsList();

        const welcomeHero = document.getElementById("chatWelcomeHero");
        if (welcomeHero) welcomeHero.style.display = "none";

        if (messagesContainer) {
            messagesContainer.innerHTML = "";
            (s.messages || []).forEach(m => {
                if (m.isHtml) {
                    const row = document.createElement("div");
                    row.className = "chat-message-row ai-row";
                    const msgId = "msg_" + Date.now() + "_" + Math.floor(Math.random()*1000);
                    row.innerHTML = `
                        <div class="message-avatar ai-avatar"><i class="fa-solid fa-robot"></i></div>
                        <div class="message-content-wrapper">
                            <span class="message-sender-name">TrafficVision AI</span>
                            <div class="message-bubble ai-bubble" id="${msgId}">${m.text}</div>
                            <div class="message-actions-toolbar">
                                <button type="button" class="msg-action-btn copy-btn" onclick="copyMessageText('${msgId}')">
                                    <i class="fa-regular fa-copy"></i> <span>Copy</span>
                                </button>
                                <button type="button" class="msg-action-btn speak-btn" onclick="speakMessageText('${msgId}')">
                                    <i class="fa-solid fa-volume-high"></i>
                                </button>
                            </div>
                        </div>
                    `;
                    messagesContainer.appendChild(row);
                } else {
                    appendMessage(m.role, m.text);
                }
            });
            scrollToBottom();
        }
    }

    function startNewSession() {
        currentSessionId = Date.now().toString();
        renderSessionsList();

        if (messagesContainer) {
            messagesContainer.innerHTML = "";
        }

        const welcomeHero = document.getElementById("chatWelcomeHero");
        if (welcomeHero) welcomeHero.style.display = "flex";

        if (chatInput) {
            chatInput.value = "";
            chatInput.focus();
        }
    }

    function deleteCurrentSession() {
        const sessions = getSessions();
        delete sessions[currentSessionId];
        saveSessions(sessions);
        startNewSession();
    }

    window.deleteSessionById = function(id, event) {
        if (event) event.stopPropagation();
        const sessions = getSessions();
        delete sessions[id];
        saveSessions(sessions);
        if (id === currentSessionId) {
            startNewSession();
        } else {
            renderSessionsList();
        }
    };

    function exportCurrentConversation() {
        const sessions = getSessions();
        const s = sessions[currentSessionId];
        if (!s || !s.messages || s.messages.length === 0) {
            alert("No messages to export yet.");
            return;
        }

        let exportText = `# TrafficVision AI Intelligence Analysis Transcript\nDate: ${new Date().toLocaleString()}\nSession ID: ${currentSessionId}\n\n---\n\n`;
        s.messages.forEach(m => {
            const sender = m.role === 'user' ? '👤 USER' : '🤖 TRAFFICVISION AI';
            const cleanText = m.isHtml ? m.text.replace(/<[^>]*>?/gm, '') : m.text;
            exportText += `### ${sender}\n${cleanText}\n\n`;
        });

        const blob = new Blob([exportText], { type: "text/markdown" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `TrafficVision_Transcript_${currentSessionId}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // Global action helpers
    window.sendPrompt = function (text) {
        if (chatInput) {
            chatInput.value = text;
            submitUserQuery();
        }
    };

    window.copyMessageText = function (msgId) {
        const bubble = document.getElementById(msgId);
        if (!bubble) return;
        const textToCopy = bubble.innerText;
        navigator.clipboard.writeText(textToCopy).then(() => {
            const btn = bubble.parentElement.querySelector(".copy-btn");
            if (btn) {
                btn.innerHTML = `<i class="fa-solid fa-check text-emerald"></i> <span style="color:#10B981">Copied!</span>`;
                setTimeout(() => {
                    btn.innerHTML = `<i class="fa-regular fa-copy"></i> <span>Copy</span>`;
                }, 2000);
            }
        });
    };

    window.speakMessageText = function (msgId) {
        const bubble = document.getElementById(msgId);
        if (!bubble || !('speechSynthesis' in window)) return;
        
        if (window.speechSynthesis.speaking) {
            window.speechSynthesis.cancel();
            return;
        }

        const utterance = new SpeechSynthesisUtterance(bubble.innerText);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        window.speechSynthesis.speak(utterance);
    };

    window.voteMessage = function (btn, type) {
        const row = btn.closest(".message-actions-toolbar");
        if (!row) return;
        row.querySelectorAll(".msg-action-btn").forEach(b => b.classList.remove("active-vote"));
        btn.classList.add("active-vote");
    };

    // Initial render of sessions list
    renderSessionsList();
}
