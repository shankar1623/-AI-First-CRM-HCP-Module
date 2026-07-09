import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

export function sendChatMessage(sessionId, message, formData) {
  return apiClient
    .post("/api/chat", { session_id: sessionId, message, form_data: formData })
    .then((res) => res.data);
}

export function resetChatSession(sessionId) {
  return apiClient.post(`/api/chat/reset/${sessionId}`);
}

export function saveInteraction(formData) {
  return apiClient.post("/api/interactions", formData).then((res) => res.data);
}
