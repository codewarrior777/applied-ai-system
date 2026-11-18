# Model Card — PawPal+ AI System

## 1. Design Choices and Tradeoffs

### System Architecture

PawPal+ has four core classes that separate concerns cleanly:

- **Task** — Data class. Pure representation of a single care activity.
- **Pet** — Data class. Holds pet details and its task list.
- **Owner** — Data class. Holds multiple pets and provides `get_all_tasks()`.
- **Scheduler** — Service class. Contains algorithms that operate on tasks.

**Why this split?** Data classes only store data, while the Scheduler holds the logic. This allows testing algorithms in isolation without a full Owner/Pet hierarchy.

### Algorithm Tradeoffs

- **`sort_by_time()`**: Uses lexicographic string sort ("HH:MM") for simplicity and JSON-friendliness. Tradeoff: no timezone/seconds granularity.
- **`detect_conflicts()`**: Pairwise O(n²) comparison. Simple and correct for small inputs (< 20 tasks). Would refactor to a hashmap for larger scale.
- **`handle_recurring()`**: Returns a new Task instance (immutable) rather than mutating. Keeps history intact and is a pure function.

---

## 2. AI Collaboration Reflection (Phase 2 & 4)

### What the AI suggested (Phase 2)

When designing the four-class system, the AI suggested adding a **fifth class: `Recurrence`**. **Why I rejected it:** It added unnecessary indirection for a 3-line function. I kept `handle_recurring` on the `Scheduler` class.

### AI Integration in Phase 4 (LLM Agent)

For the Applied AI System, I integrated an LLM (via OpenRouter) to parse natural language tasks. The AI helped design the `system_prompt` and the JSON schema. However, relying solely on the LLM was risky due to hallucinations (e.g., invalid times like "25:00" or unknown pets).

**Guardrails Implemented:**

1. **API Key Check:** Falls back to Regex if no API key is present.
2. **Markdown Stripping:** Cleans JSON blocks from the LLM response.
3. **Time Validation:** Uses regex to ensure the time is valid (00:00 to 23:59). If invalid, defaults to "12:00".
4. **Pet Validation:** Ensures the parsed pet name exists in the user's list, otherwise sets it to `None`.
5. **Frequency & Priority Validation:** Ensures the LLM only returns valid values for these fields.

### The Reliability Fallback

The most important engineering decision was the **Regex Fallback**. If the LLM API fails (timeout, 429 rate limit, or 500 error), the system automatically falls back to `nl_parser.py`. This guarantees the app never crashes and always provides a structured task, even if the AI is unavailable.

**Testing:** I wrote tests using `pytest` and `unittest.mock` to simulate API failures and validate all guardrails without spending tokens.

---

## 3. Baseline vs. Specialized Output Comparison (Fine-tuning reflection)

The professor asked for a comparison between a baseline (generic) output and a specialized (prompted) output.

- **Baseline Prompt:** "Extract the task from this text."
- **Specialized Prompt (Used in PawPal+):** A strict JSON schema with exact keys, default values ("12:00" for time, "medium" for priority), and a list of known pet names.

**Comparison:**
Without the specialized prompt, the LLM would return conversational text (e.g., "Sure, I can help you walk Cooper at 7am.") or inconsistent JSON. By using the structured prompt with explicit schema instructions and guardrails, the output becomes 100% deterministic and directly parsable by Python, eliminating the need for post-processing text. This specialization is why the system can reliably create `Task` objects from free-form text.