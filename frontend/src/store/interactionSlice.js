import { createSlice } from "@reduxjs/toolkit";

const emptyForm = {
  hcp_name: "",
  interaction_type: "",
  date: "",
  time: "",
  attendees: "",
  topics_discussed: "",
  materials_shared: "",
  samples_distributed: "",
  sentiment: "",
  outcomes: "",
  follow_up_actions: "",
  competitors_mentioned: "",
};

const interactionSlice = createSlice({
  name: "interaction",
  initialState: {
    form: { ...emptyForm },
    savedStatus: "idle", // idle | saving | saved | error
  },
  reducers: {
    formUpdated(state, action) {
      state.form = { ...state.form, ...action.payload };
    },
    formReset(state) {
      state.form = { ...emptyForm };
      state.savedStatus = "idle";
    },
    saveStatusSet(state, action) {
      state.savedStatus = action.payload;
    },
  },
});

export const { formUpdated, formReset, saveStatusSet } = interactionSlice.actions;
export default interactionSlice.reducer;
