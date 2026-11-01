# Reflection — PawPal+

## 1. Design Choices and Tradeoffs

### System Architecture

PawPal+ has four core classes that separate concerns cleanly:

- **Task** — Data class. Pure representation of a single care activity.
- **Pet** — Data class. Holds pet details and its task list.
- **Owner** — Data class. Holds multiple pets and provides `get_all_tasks()`
  as a convenience for combined access.
- **Scheduler** — Service class. Contains **algorithms** that operate on tasks.

**Why this split?**
The design follows a strict separation: data classes (Task, Pet, Owner) only
store data, while the Scheduler holds the logic. This means the algorithms can
be tested in isolation with plain lists of tasks, without needing to set up a
full Owner/Pet hierarchy every time.

### Algorithm Tradeoffs

#### `sort_by_time()` — Lexicographic string sort

I chose to store task times as strings in `"HH:MM"` format (e.g. `"07:00"`,
`"14:30"`) instead of Python `datetime.time` objects.

**Tradeoff:**
- ✅ **Pro:** Simpler serialization (JSON-friendly), simpler UI input via
  Streamlit's `st.time_input` + `.strftime("%H:%M")`.
- ✅ **Pro:** String sort works correctly for `"HH:MM"` because zero-padded
  24-hour strings sort chronologically.
- ❌ **Con:** Does not handle `"7:00"` vs `"07:00"` (would sort incorrectly).
- ❌ **Con:** No timezone or seconds granularity.

**Decision:** The simplicity win outweighs the loss of granularity for this use case.

#### `detect_conflicts()` — Pairwise O(n²) comparison

For each pair of tasks, compare their `.time` fields.

**Tradeoff:**
- ✅ **Pro:** Simple, obviously correct, no external dependencies.
- ✅ **Pro:** Handles any size input without crashing.
- ❌ **Con:** O(n²) — for 100 tasks, that's 4,950 comparisons.
- ❌ **Con:** Only detects **exact** time matches, not overlapping durations
  (since tasks don't have a duration field).

**Decision:** For a single owner with 2-5 pets and a handful of tasks per day,
n is small (< 20), so O(n²) is fine. If the app scaled to hundreds of tasks,
I'd refactor to group by time using a hashmap (O(n)).

#### `handle_recurring()` — Immutable task creation

When a recurring task is completed, `handle_recurring()` returns a **new**
Task instance for the next occurrence instead of mutating the original.

**Tradeoff:**
- ✅ **Pro:** Keeps history intact — the original completion is preserved.
- ✅ **Pro:** Pure function; no side effects.
- ❌ **Con:** The caller must decide when to actually add the new task to the
  pet's task list (currently not automatic — see below).

**Decision:** Purity is preferred over convenience here. The current `main.py`
demo shows the returned task without persisting it, which is intentional —
the UI in Phase 3 could later expose a "generate next occurrence" button.

---

## 2. AI Collaboration Reflection (Phase 2)

### What the AI suggested

When I asked ChatGPT to design the four-class system, it suggested adding a
**fifth class: `Recurrence`** — a separate class that would own the logic for
generating recurring tasks.

**Why I rejected it:**
The `Recurrence` class added a layer of indirection for what is essentially
a 3-line function (`handle_recurring`). It would require wiring the class into
`Task`, `Scheduler`, and the UI, adding surface area without proportional
benefit. The Mermaid UML from Phase 1 already specified **four classes**, and
adding a fifth would mean updating the UML and the README.

I kept `handle_recurring` on the `Scheduler` class — the "brain" that already
owns algorithmic behavior.

### What the AI got right

The AI correctly identified that **`Owner.get_all_tasks()` should combine
tasks across all pets** using a nested list comprehension:

```python
return [task for pet in self.pets for task in pet.tasks]