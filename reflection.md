# PawPal+ Project Reflection

## 1. System Design

Three core actions that the user should be able to perfom include:
1. Entering pet/s name/s. 
2. Blocking out time to take the pet on a walk. 
3. See a clear, well-explained daily plan. 

**a. Initial design**

- Briefly describe your initial UML design.
Four main objects with attributes and methods: 

    * Owner has a pet/s

    * Pet/s follows schedule and has tasks

    * Schedule has tasks and organizes tasks

- What classes did you include, and what responsibilities did you assign to each?

- Owner: name, email, phone, pet
    Responsibilities: Managing pets

- Pet: name, species, breed, age
    Responsibilities: Following a schedule 

-  Schedule: combination of tasks that change daily
    Responsibilities: Organizing and filtering tasks

- Tasks: walking, feeding, grooming, enrichment
    Responsibilities: Holding the tasks and managing there states

**b. Design changes**

Bottlenecks and Missing Relationships in UML draft as suggested by Claude:
- Task has no date field but two methods depend on a date.
- Pet follows a schedule, but Pet has no schedule attricute.
- No back references: Pet does not know its Owner and Task does not know which Pet or Schedule it belongs to.



- Did your design change during implementation?

Yes. My original UML described relationships in words (Pet "follows" a Schedule, Task "belongs to" a Pet), but when I turned it into code those links did not actually exist as attributes, and some methods had nothing to work with.

- If yes, describe at least one change and why you made it.

Changes I made to my original idea with the help of Claude:

1. Added a date field to Task. My original Task only held a title, type, and completion state, but two methods depended on a date that did not exist: `reschedule(new_date)` had nowhere to store the new date, and `Schedule.get_tasks_for_day(day)` had no task date to filter on. I added a `due_date` so those methods can actually work.

2. Added the Pet to Schedule link. My UML said a Pet "follows" a Schedule, but in code Pet had no `schedule` attribute, so the relationship only existed on paper. I added it so a pet is actually connected to its schedule.

3. Added back-references. Originally I could only navigate top-down (Owner to Pet to Task). There was no way to go from a Task back to its Pet, or from a Pet back to its Owner, so I noted the need to store those references.

Why: these changes came from reviewing the skeleton before implementing. The gaps meant methods I had already written stubs for could not be completed as designed, so fixing the relationships first kept the code and the UML in sync.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

My original scheduler had several small, separately-named methods for querying tasks: `pending_tasks()`, `completed_tasks()`, `tasks_for_pet()`, and `tasks_by_frequency()`. When I asked Claude how to simplify, it suggested consolidating all of them into a single, flexible `filter_tasks(pet_name=..., status=..., frequency=...)` method that takes the filter I want as arguments. The tradeoff is between **many explicit named methods** and **one general-purpose method**.

The consolidated version is DRY (one place defines the filtering logic instead of four) and easy to extend — adding a new filter is a new keyword argument rather than a whole new method. The cost is that it relies on "stringly-typed" arguments like `status="pending"`: a typo such as `status="pendign"` is not caught until it fails at runtime, whereas calling a method named `pending_tasks()` cannot be mistyped silently and reads more clearly at the call site.

I did **not** accept the full consolidation as-is. Instead I added `filter_tasks(pet_name=..., status=...)` only for the one case that genuinely needed a *combined* query — filtering by pet and completion status together, which the Streamlit UI uses — and kept the simple named methods (`pending_tasks()`, `completed_tasks()`, `tasks_for_pet()`, `tasks_by_frequency()`) as their own small, clearly-named methods rather than folding everything into one string-argument method. Two of them wouldn't have fit cleanly anyway: `tasks_for_pet()` takes a `Pet` object (matching by identity, not by name, so two same-named pets never collide), and `tasks_by_frequency()` covers a filter `filter_tasks()` deliberately doesn't. Collapsing those into one stringly-typed method would have made the call sites less clear and less precise. I also decided the heavier "most Pythonic" option Claude mentioned — replacing the status strings with an `Enum` — was more machinery than this small project needs.

- Why is that tradeoff reasonable for this scenario?

For a project this size, readability and correctness at the call site matter more than maximum flexibility. Keeping the small named methods means the demo and UI code reads plainly (`scheduler.pending_tasks()`), while `filter_tasks()` handles the one place a combined pet-and-status query is actually needed. Deferring the `Enum` avoids adding abstraction I do not yet need. If the number of filter combinations grew a lot, I would revisit — either routing the named methods through `filter_tasks()` or introducing the `Enum` for type safety.

---

## 3. AI Collaboration

**a. How you used AI — and which features were most effective**

I used Claude Code (an agentic AI coding assistant) across every phase: design
review, implementation, refactoring, testing, and documentation. The features
that mattered most for building the scheduler were:

- **Whole-file code review.** Claude could read all of `pawpal_system.py` at
  once and summarize the core behaviors back to me, which is how I decided what
  was worth testing. That was far faster than re-reading it myself.
- **Agentic test generation *and execution*.** The biggest win was that Claude
  didn't just write the 27 pytest cases — it ran `pytest` in the terminal,
  showed me the passing output, and fixed the small issues (like unused
  variables) itself. Being able to generate a test and immediately see it go
  green tightened the loop a lot.
- **Running `main.py` to produce real output.** When I wanted sample output for
  the README, Claude ran the script and pasted the *actual* terminal output
  instead of guessing, which caught that an older README sample was stale.
- **Inline diff edits.** Editing files as small, reviewable diffs (rather than
  regenerating whole files) let me see exactly what changed and keep control.

The prompts that worked best were **specific and verifiable**: "list the core
behaviors to test," "what edge cases matter for a scheduler with sorting and
recurring tasks," and "wire the display logic to the Scheduler methods." Vague
prompts produced vague code; concrete ones produced code I could immediately
run and check.

**b. Judgment and verification — a suggestion I modified**

The clearest example is the query-method refactor described in Section 2. Claude
suggested collapsing my four named methods (`pending_tasks()`,
`completed_tasks()`, `tasks_for_pet()`, `tasks_by_frequency()`) into a single
`filter_tasks(...)` method, and also floated replacing the status strings with a
full `Enum` for type safety. I took the DRY idea but **rejected the most
aggressive version**: I kept readable, typo-proof named methods at the call
sites and deferred the `Enum` because it was more machinery than a project this
size needs. The point was to keep the design clean and legible, not maximally
abstract.

I verified AI output three ways rather than trusting it: I **ran the test suite**
(27 passing tests covering sorting, recurrence, conflicts, filtering, and edge
cases), I **ran `main.py`** to watch the real behavior end-to-end, and I **read
every diff** before accepting it. When Claude first flagged conflicting rows in
the Streamlit table by string-matching warning text, I had it switch to
comparing time values directly, because the string approach would break on
unpadded times like `"8:00"` vs `"08:00"`.

**c. How separate chat sessions kept me organized**

I ran a different chat session for each phase — design, implementation, testing,
and documentation. Starting a fresh session for testing meant the assistant's
attention (and mine) was fully on "what could break," not tangled up in the
design conversation from earlier. Each session had one clear goal, so the
context stayed focused, the suggestions stayed on-topic, and I could pick work
back up later without scrolling through unrelated history. It also made the
project feel like distinct, finishable milestones instead of one endless thread.

**d. What I learned about being the "lead architect"**

The most important lesson is that a powerful AI tool is an accelerator, not a
decision-maker. Claude could generate tests, run them, refactor, and draft docs
in seconds — but it happily produced *plausible* options (the full
consolidation, the `Enum`, the string-matching table flags) that I had to weigh
against my own goals for a clean, right-sized design. My job as lead architect
was to set the direction, ask precise questions, and **verify everything by
running it** — the tests and `main.py` were my ground truth, not the AI's
confidence. The AI made me faster; the design judgment and the accountability
for what shipped stayed mine.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
