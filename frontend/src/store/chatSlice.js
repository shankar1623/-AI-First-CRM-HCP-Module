import { createSlice } from "@reduxjs/toolkit";

const chatSlice = createSlice({
  name: "chat",
  initialState: {
    messages: [
      {
        role: "assistant",
        content:
          "Tell me about the interaction — e.g. \"Met Dr. Sarah Smith today, she showed positive interest in OncoBoost, discussed efficacy data and Phase III results. Shared the clinical brochure. She wants a follow-up in 2 weeks.\"",
      },
    ],
    badges: [],
    isSending: false,
  },
  reducers: {
    messageAdded(state, action) {
      state.messages.push(action.payload);
    },
    badgesUpdated(state, action) {
      action.payload.forEach((b) => {
        if (!state.badges.includes(b)) state.badges.push(b);
      });
    },
    sendingSet(state, action) {
      state.isSending = action.payload;
    },
    chatReset(state) {
      state.messages = [state.messages[0]];
      state.badges = [];
      state.isSending = false;
    },
  },
});

export const { messageAdded, badgesUpdated, sendingSet, chatReset } = chatSlice.actions;
export default chatSlice.reducer;
