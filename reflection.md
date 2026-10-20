# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
    - The UML design is based on an owner who can have one or more pets. Each pet has its own care tasks, and a **DailyScheduler** gathers and organizes tasks across all the pets.

- What classes did you include, and what responsibilities did you assign to each?

    - **Owner:** Stores identifying information and manages a list of pets.
    - **Pet:** Stores identifying information and manages its care tasks.
    - **CareTask:** Stores a description, title, due date, and completion status; it can be marked complete.
    - **DailyScheduler:** Gathers tasks across pets, sorts and filters them by due date, and builds a daily schedule.

**b. Design changes**

- Did your design change during implementation?
    - Yes.
- If yes, describe at least one change and why you made it.

    I clarified how pets, tasks, and owners relate to each other:
    - Each task belongs to one pet, so completion is tracked independently.
    - Scheduled tasks stay paired with their pets, so it's clear whose task it is.
    - Each owner must have at least one pet, matching the UML relationship.

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
