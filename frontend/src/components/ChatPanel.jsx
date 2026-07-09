import { useState, useRef, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { messageAdded, badgesUpdated, sendingSet } from "../store/chatSlice";
import { formUpdated } from "../store/interactionSlice";
import { sendChatMessage } from "../api/client";

const TOOL_COUNT = 5;

export default function ChatPanel({ sessionId }) {
  const dispatch = useDispatch();
  const { messages, badges, isSending } = useSelector((state) => state.chat);
  const form = useSelector((state) => state.interaction.form);
  const [input, setInput] = useState("");
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [messages]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || isSending) return;

    dispatch(messageAdded({ role: "user", content: text }));
    setInput("");
    dispatch(sendingSet(true));

    try {
      const data = await sendChatMessage(sessionId, text, form);
      dispatch(formUpdated(data.form_data));
      dispatch(badgesUpdated(data.badges || []));
      dispatch(messageAdded({ role: "assistant", content: data.reply }));
    } catch (err) {
      dispatch(
        messageAdded({
          role: "assistant",
          content:
            "Sorry, I couldn't reach the backend. Make sure the FastAPI server is running on the configured URL.",
        })
      );
    } finally {
      dispatch(sendingSet(false));
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <div className="chat-header-title">
          <strong>🤖 AI Assistant</strong>
          <span className="chat-status">{TOOL_COUNT} tools active</span>
        </div>
        <div className="chat-subtitle">Log Interaction via chat</div>
      </div>

      {badges.length > 0 && (
        <div className="badge-row">
          {badges.map((b) => (
            <span key={b} className={`badge ${b}`}>
              {b}
            </span>
          ))}
        </div>
      )}

      <div className="chat-messages" ref={scrollRef}>
        {messages.map((m, i) => (
          <div key={i} className={`chat-bubble ${m.role === "user" ? "user" : "assistant"}`}>
            {m.role === "assistant" && <span className="bubble-label">Logged interaction</span>}
            {m.content}
          </div>
        ))}
        {isSending && (
          <div className="chat-bubble assistant">
            <span className="bubble-label">Thinking…</span>
            Extracting details and updating the form…
          </div>
        )}
      </div>

      <div className="chat-input-row">
        <textarea
          placeholder="Describe interaction (e.g. 'Met Dr. Jones, discussed drug X, very positive')"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button className="btn primary" onClick={handleSend} disabled={isSending}>
          ⚡ Log
        </button>
      </div>
    </div>
  );
}
