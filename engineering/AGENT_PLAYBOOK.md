# Standard Engineering Workflow

1. Select backlog task.

2. Read engineering context.
   - CONSTITUTION.md
   - AGENT_PLAYBOOK.md
   - TASK_TEMPLATE.md

   Re-read these documents:
   - when starting a new Epic;
   - after long inactivity;
   - whenever explicitly requested.

3. Complete TASK_TEMPLATE.

4. Implement the task.

5. Verify acceptance criteria.

6. Update project artifacts.
   - backlog.md
   - engineering/CHANGELOG.md (when applicable)

7. Produce a Task Completion Report.

8. Wait for independent Engineering Review.

9. Address review comments if required.

10. Merge only after review approval.

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

# Engineering Review

The implementation engineer does not self-approve changes.

After every implementation task:

- provide the Task Completion Report;
- submit the updated project for independent review;
- wait for review outcome.

Possible outcomes:

APPROVED

APPROVED WITH NOTES

CHANGES REQUESTED

Merge only after approval.

# Engineering Context Synchronization

Engineering context should be refreshed:

- at the beginning of every new Epic;
- after long inactivity;
- whenever requested by the project lead.

The purpose is to ensure alignment with the current Constitution, Playbook, Task Template and backlog.

Context synchronization itself must not modify project code or engineering documentation.