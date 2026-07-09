import { useMemo } from "react";
import { v4 as uuidv4 } from "uuid";
import Header from "./components/Header";
import InteractionForm from "./components/InteractionForm";
import ChatPanel from "./components/ChatPanel";

export default function App() {
  const sessionId = useMemo(() => uuidv4(), []);

  return (
    <div className="app-shell">
      <Header />
      <div className="split-layout">
        <InteractionForm sessionId={sessionId} />
        <ChatPanel sessionId={sessionId} />
      </div>
    </div>
  );
}
