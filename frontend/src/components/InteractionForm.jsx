import { useDispatch, useSelector } from "react-redux";
import { formReset, saveStatusSet } from "../store/interactionSlice";
import { chatReset } from "../store/chatSlice";
import { saveInteraction, resetChatSession } from "../api/client";

function Field({ label, value, fullWidth }) {
  return (
    <div className={`field${fullWidth ? " full-width" : ""}`}>
      <span className="field-label">{label}</span>
      <div className={`field-value${!value ? " empty" : ""}`}>
        {value || "—"}
      </div>
    </div>
  );
}

export default function InteractionForm({ sessionId }) {
  const dispatch = useDispatch();
  const form = useSelector((state) => state.interaction.form);
  const savedStatus = useSelector((state) => state.interaction.savedStatus);

  const handleReset = async () => {
    dispatch(formReset());
    dispatch(chatReset());
    try {
      await resetChatSession(sessionId);
    } catch (e) {
      // non-fatal
    }
  };

  const handleSave = async () => {
    dispatch(saveStatusSet("saving"));
    try {
      await saveInteraction(form);
      dispatch(saveStatusSet("saved"));
    } catch (e) {
      dispatch(saveStatusSet("error"));
    }
  };

  return (
    <div className="form-panel">
      <div className="card">
        <p className="card-title">Interaction Details</p>
        <div className="field-grid">
          <Field label="HCP Name" value={form.hcp_name} />
          <Field label="Interaction Type" value={form.interaction_type} />
          <Field label="Date" value={form.date} />
          <Field label="Time" value={form.time} />
          <Field label="Attendees" value={form.attendees} fullWidth />
        </div>
      </div>

      <div className="card">
        <p className="card-title">Topics Discussed</p>
        <Field label="Topics Discussed" value={form.topics_discussed} fullWidth />
        <span className="chat-hint">✎ Or describe verbally via AI chat →</span>
      </div>

      <div className="card">
        <p className="card-title">Materials Shared / Samples Distributed</p>
        <div className="field-grid">
          <Field label="Materials Shared" value={form.materials_shared} fullWidth />
          <Field label="Samples Distributed" value={form.samples_distributed} fullWidth />
        </div>
      </div>

      <div className="card">
        <p className="card-title">Observed / Inferred HCP Sentiment</p>
        <div className="sentiment-row">
          {["Positive", "Neutral", "Negative"].map((s) => (
            <div
              key={s}
              className={`sentiment-chip ${s.toLowerCase()}${
                form.sentiment === s ? " active" : ""
              }`}
            >
              {s === "Positive" ? "🙂" : s === "Negative" ? "🙁" : "😐"} {s}
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <p className="card-title">Outcomes</p>
        <Field label="Outcomes" value={form.outcomes} fullWidth />
      </div>

      <div className="card">
        <p className="card-title">Follow-up Actions</p>
        <Field label="Follow-up Actions" value={form.follow_up_actions} fullWidth />
      </div>

      {form.competitors_mentioned ? (
        <div className="card">
          <p className="card-title">Competitors Mentioned</p>
          <Field label="Competitors Mentioned" value={form.competitors_mentioned} fullWidth />
        </div>
      ) : null}

      <div className="form-actions">
        <button className="btn" onClick={handleReset}>⟲ Reset Form</button>
        <button className="btn primary" onClick={handleSave} disabled={savedStatus === "saving"}>
          {savedStatus === "saving"
            ? "Saving…"
            : savedStatus === "saved"
            ? "✓ Saved"
            : "⬆ Save to DB"}
        </button>
      </div>
    </div>
  );
}
