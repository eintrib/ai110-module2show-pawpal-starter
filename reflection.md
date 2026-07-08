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
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

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
