# Agent evidence and its limits

- `original_prompt_and_response_excerpts.json`: selected original visible user instructions and assistant responses, including the horizon correction, model recommendation, window choice and 381-origin start. Original message IDs and turn timestamps are retained; local paths are redacted.
- `original_tool_call_excerpts.json`: four original tool calls and their matching outputs, extracted separately from the archived session rollout. They document horizon-code corrections and subsequent checks; host paths are redacted. No private reasoning, system/developer messages or unrelated session content is included.
- `original_six_session_design.json`: original archived design for the five-to-six-session correction; describes an earlier research stage.
- `six_session_correction.md`: explanation of the correction and its code checks.
- `model_recommendation_and_checks.md`: model recommendation and verification evidence.
- `reproduction_tool_calls.json` and `execution_transcript.txt`: actual commands, timestamps and captured outputs from the present packaging/reproduction run, clearly separate from original historical tool calls.

These are selected evidence extracts, not a complete conversation or research
history. They do not establish human approval. Earlier exploratory results are
not substituted for the final archived report results.
