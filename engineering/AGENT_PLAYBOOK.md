# AGENT_PLAYBOOK.md

# Standard Engineering Workflow

1. Select the assigned backlog task.

2. Synchronize engineering context.

   Read:

   - CONSTITUTION.md
   - AGENT_PLAYBOOK.md
   - TASK_TEMPLATE.md

   Re-read these documents:

   - when starting a new Epic;
   - after long inactivity;
   - whenever explicitly requested by the board.

3. Complete TASK_TEMPLATE.

4. Evaluate the current repository state before implementing.

   - Verify whether the requested functionality already exists.
   - Reuse existing implementations whenever appropriate.
   - Do not duplicate completed work.

5. Implement only the assigned scope.

   During implementation:

   - avoid unrelated refactoring;
   - avoid expanding task scope;
   - record architectural observations as Engineering Debt rather than fixing them unless explicitly requested.

6. Verify acceptance criteria.

   At minimum:

   - tests pass;
   - acceptance criteria satisfied;
   - no obvious regressions introduced.

7. Update project artifacts where applicable.

   Examples:

   - backlog.md
   - engineering/CHANGELOG.md

8. Produce a Task Completion Report.

9. Wait for independent Engineering Review.

10. Address review comments if required.

11. Merge only after review approval.

---

# Task Completion Report

Every completed implementation task must end with a concise report.

Maximum size:

approximately 200 tokens.

Template:

Task:

Result:

Files Changed:

Acceptance Criteria:

Validation:

Backlog:

Changelog:

Known Limitations:

Risk Assessment:

LOW / MEDIUM / HIGH

Next Suggested Task:

---

# Engineering Review

The implementation engineer never self-approves changes.

After every implementation task:

- provide the Task Completion Report;
- submit the updated project for independent review;
- wait for the review outcome.

Possible outcomes:

- APPROVED
- APPROVED WITH NOTES
- CHANGES REQUESTED

Merge only after approval.

---

# Engineering Context Synchronization

Engineering context should be refreshed:

- at the beginning of every new Epic;
- after long inactivity;
- whenever requested by the project lead.

The purpose is to ensure alignment with:

- CONSTITUTION.md
- AGENT_PLAYBOOK.md
- TASK_TEMPLATE.md
- backlog.md

Context synchronization itself must not:

- modify project code;
- modify engineering documentation;
- restructure the backlog.

---

# Planning Tasks

Planning, architecture, review and release-management tasks must not implement code.

Such tasks may:

- analyze the repository;
- analyze the backlog;
- produce implementation plans;
- produce release plans;
- produce review reports;
- identify risks;
- identify dependencies.

They must not:

- create implementation changes;
- perform refactoring;
- expand project scope.

---

# Release Stabilization

Once the project is declared **Feature Complete**, development enters Release Stabilization.

During Release Stabilization:

- no new product features should be added;
- only release engineering, testing, packaging, documentation and critical bug fixes should be performed;
- architectural improvements should be deferred unless required to unblock release.

---

# Engineering Debt

When implementation exposes architectural inconsistencies:

- record them;
- prioritize them;
- implement them only when explicitly requested.

Do not expand the scope of the current task.

---

# Board Decisions

Board comments are discussion.

Only explicit board decisions change project state.

When a confirmation interaction expires, do not assume rejection.

Wait for an explicit board decision before changing project status.

---

# Parallel Execution

Unless explicitly approved by the board:

- assume a single implementation engineer;
- plan work sequentially;
- do not optimize plans for parallel execution.

Parallel implementation should only be proposed when sufficient engineering resources are explicitly available.