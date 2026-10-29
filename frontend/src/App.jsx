
import { useCallback, useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function createSessionId() {
  return crypto.randomUUID();
}

function formatDate(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";

  const now = new Date();
  const isToday = date.toDateString() === now.toDateString();

  if (isToday) {
    return date.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  return date.toLocaleDateString([], {
    month: "short",
    day: "numeric",
  });
}

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [chats, setChats] = useState([]);
  const [sessionId, setSessionId] = useState(createSessionId);
  const [loading, setLoading] = useState(false);
  const [loadingChats, setLoadingChats] = useState(true);
  const [error, setError] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const refreshChats = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/chats`);
      if (!response.ok) {
        throw new Error(`Could not load chats (${response.status})`);
      }

      const data = await response.json();
      setChats(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Chat history error:", err);
    } finally {
      setLoadingChats(false);
    }
  }, []);

  useEffect(() => {
    refreshChats();
  }, [refreshChats]);

  async function sendMessage(event, suggestedMessage) {
    event?.preventDefault();

    const text = (suggestedMessage ?? message).trim();
    if (!text || loading) return;

    const currentSessionId = sessionId;

    setMessages((previous) => [
      ...previous,
      { role: "user", content: text },
    ]);
    setMessage("");
    setError("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          session_id: currentSessionId,
        }),
      });

      if (!response.ok) {
        const detail = await response.text();
        throw new Error(detail || `Server returned ${response.status}`);
      }

      const data = await response.json();

      setSessionId(data.session_id);
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.response,
          intent: data.intent,
        },
      ]);

      await refreshChats();
    } catch (err) {
      console.error("Message error:", err);
      setError(
        "Couldn't send your message. Check that FastAPI and PostgreSQL are running, then try again."
      );
    } finally {
      setLoading(false);
    }
  }

  function startNewChat() {
    setSessionId(createSessionId());
    setMessages([]);
    setMessage("");
    setError("");
    setSidebarOpen(false);
  }

  async function openChat(chat) {
    if (loading) return;

    setSessionId(chat.session_id);
    setMessages([]);
    setMessage("");
    setError("");
    setSidebarOpen(false);
    setLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/chats/${encodeURIComponent(chat.session_id)}`
      );

      if (!response.ok) {
        throw new Error(`Could not open chat (${response.status})`);
      }

      const data = await response.json();
      setMessages(Array.isArray(data.messages) ? data.messages : []);
    } catch (err) {
      console.error("Open chat error:", err);
      setError("Couldn't open this conversation. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  const activeChat = chats.find(
    (chat) => chat.session_id === sessionId
  );

  return (
    <div className="app-shell">
      {sidebarOpen && (
        <button
          className="sidebar-backdrop"
          aria-label="Close sidebar"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="sidebar-top">
          <a className="brand" href="#home" onClick={(event) => {
            event.preventDefault();
            startNewChat();
          }}>
            <div className="brand-mark">✳</div>
            <div className="brand-copy">
              <strong>AI Assistant</strong>
              <span>Your intelligent space</span>
            </div>
          </a>

          <button
            className="icon-button sidebar-close"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close sidebar"
          >
            ×
          </button>
        </div>

        <button
          className="new-chat"
          onClick={startNewChat}
          disabled={loading}
        >
          <span className="new-chat-icon">＋</span>
          <span>New conversation</span>
          <kbd>⌘</kbd>
        </button>

        <div className="history-heading">
          <span>YOUR WORKSPACE</span>
          <span className="history-count">{chats.length}</span>
        </div>

        <div className="chat-history">
          {loadingChats ? (
            <div className="sidebar-message">
              <span className="mini-spinner" />
              Loading conversations...
            </div>
          ) : chats.length === 0 ? (
            <div className="empty-history">
              <div className="empty-history-icon">▤</div>
              <strong>Your history starts here</strong>
              <p>Your conversations will appear here after your first message.</p>
            </div>
          ) : (
            chats.map((chat) => (
              <button
                key={chat.session_id}
                className={`history-item ${
                  chat.session_id === sessionId ? "history-item-active" : ""
                }`}
                onClick={() => openChat(chat)}
                disabled={loading}
                title={chat.title || "New Chat"}
              >
                <span className="history-item-icon">◌</span>
                <span className="history-item-text">
                  <span className="history-title">
                    {chat.title || "New Chat"}
                  </span>
                  <span className="history-date">
                    {formatDate(chat.updated_at || chat.created_at)}
                  </span>
                </span>
                {chat.session_id === sessionId && (
                  <span className="active-indicator" />
                )}
              </button>
            ))
          )}
        </div>

        <div className="sidebar-footer">
          <div className="provider-mark">G</div>
          <div className="provider-copy">
            <strong>Powered by Groq</strong>
            <span><i /> AI engine connected through your API</span>
          </div>
          <span className="footer-sparkle">✦</span>
        </div>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <div className="topbar-left">
            <button
              className="icon-button menu-button"
              onClick={() => setSidebarOpen(true)}
              aria-label="Open sidebar"
            >
              ☰
            </button>
            <div className="page-context">
              <span className="context-eyebrow">PERSONAL AI WORKSPACE</span>
              <h1>{activeChat?.title || "AI Assistant"}</h1>
            </div>
          </div>

          <div className="topbar-right">
            <span className="status-pill">
              <i />
              Ready to help
            </span>
            <div className="profile-avatar">AI</div>
          </div>
        </header>

        <section className="chat-panel">
          <div className="chat-content">
            {messages.length === 0 && !loading && (
              <div className="welcome-screen">
                <div className="welcome-orbit">
                  <div className="welcome-icon">✳</div>
                  <span className="orbit-dot orbit-dot-one" />
                  <span className="orbit-dot orbit-dot-two" />
                </div>

                <p className="eyebrow">A LITTLE MORE INTELLIGENCE</p>
                <h2>
                  Good to see you,
                  <br />
                  <span></span>
                </h2>
                <p className="welcome-description">
                  What would you like to explore today? Ask a question,
                  build something, or learn a new concept.
                </p>

                <div className="suggestion-grid">
                  <button
                    className="suggestion-card"
                    onClick={() => sendMessage(null, "Explain Python variables with examples")}
                    disabled={loading}
                  >
                    <span className="suggestion-icon violet">{"</>"}</span>
                    <span>
                      <strong>Learn Python</strong>
                      <small>Understand concepts with examples</small>
                    </span>
                    <span className="suggestion-arrow">↗</span>
                  </button>

                  <button
                    className="suggestion-card"
                    onClick={() => sendMessage(null, "Help me build a FastAPI endpoint step by step")}
                    disabled={loading}
                  >
                    <span className="suggestion-icon blue">⌘</span>
                    <span>
                      <strong>Build an API</strong>
                      <small>Create a backend step by step</small>
                    </span>
                    <span className="suggestion-arrow">↗</span>
                  </button>

                  <button
                    className="suggestion-card"
                    onClick={() => sendMessage(null, "Explain how large language models work in simple words")}
                    disabled={loading}
                  >
                    <span className="suggestion-icon orange">✧</span>
                    <span>
                      <strong>Explore AI</strong>
                      <small>Make complex ideas simple</small>
                    </span>
                    <span className="suggestion-arrow">↗</span>
                  </button>

                  <button
                    className="suggestion-card"
                    onClick={() => sendMessage(null, "Review my approach to building a React frontend connected to FastAPI")}
                    disabled={loading}
                  >
                    <span className="suggestion-icon green">⌘</span>
                    <span>
                      <strong>Build a project</strong>
                      <small>Plan your next development task</small>
                    </span>
                    <span className="suggestion-arrow">↗</span>
                  </button>
                </div>
              </div>
            )}

            {messages.map((item, index) => (
              <div className={`message-row ${item.role}`} key={`${sessionId}-${index}`}>
                <div className={`avatar ${item.role}`}>
                  {item.role === "user" ? "AI" : "✳"}
                </div>

                <div className="message-body">
                  <div className="message-heading">
                    <strong>
                      {item.role === "user" ? "You" : "AI Assistant"}
                    </strong>
                    {item.intent && (
                      <span className="intent-tag">{item.intent}</span>
                    )}
                  </div>

                  <div className="markdown-content">
                    {item.role === "assistant" ? (
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {item.content}
                      </ReactMarkdown>
                    ) : (
                      <p>{item.content}</p>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {loading && (
              <div className="message-row assistant">
                <div className="avatar assistant">✳</div>
                <div className="message-body">
                  <div className="message-heading">
                    <strong>AI Assistant</strong>
                    <span className="thinking-label">Thinking</span>
                  </div>
                  <div className="typing-indicator">
                    <span />
                    <span />
                    <span />
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="error-message">
                <span>!</span>
                <p>{error}</p>
                <button onClick={() => setError("")}>Dismiss</button>
              </div>
            )}
          </div>

          <div className="composer-area">
            <form className="composer" onSubmit={(event) => sendMessage(event)}>
              <textarea
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                onKeyDown={(event) => {
                  if (
                    event.key === "Enter" &&
                    !event.shiftKey &&
                    !event.nativeEvent.isComposing
                  ) {
                    event.preventDefault();
                    sendMessage();
                  }
                }}
                placeholder="Message your Assistant..."
                rows={1}
                aria-label="Message AI Assistant"
                disabled={loading}
              />
              <div className="composer-toolbar">
                <span className="composer-note">
                  <span className="composer-sparkle">✦</span>
                  Responses powered by Groq
                </span>
                <button
                  className="send-button"
                  type="submit"
                  disabled={loading || !message.trim()}
                  aria-label="Send message"
                >
                  {loading ? <span className="mini-spinner" /> : "↑"}
                </button>
              </div>
            </form>
            <p className="composer-hint">
              AI can make mistakes. Verify important information. <span>·</span> Enter to send
            </p>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
