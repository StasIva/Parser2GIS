# Task Template

Use this template for every engineering task assigned to an AI agent.

---

# Title

Provide a short, action-oriented title.

---

# Objective

Describe the business or technical goal.

Explain why this task exists.

---

# Context

Describe the current state.

Include:

- relevant architecture
- existing implementation
- previous work
- assumptions

Reference existing project documentation whenever possible.

---

# Constraints

The implementation MUST comply with:

- ENGINEERING_CONSTITUTION.md
- engineering/CODE_REVIEW_CHECKLIST.md
- engineering/AGENT_PLAYBOOK.md

Additional constraints:

- Preserve existing architecture.
- Prefer extending existing code.
- Avoid unnecessary abstractions.
- Keep changes as small as possible.
- Maintain backwards compatibility unless explicitly stated otherwise.

---

# Expected Deliverables

Specify all expected outputs.

Examples:

- source code
- tests
- documentation
- migrations
- configuration updates

---

# Acceptance Criteria

Define objective completion criteria.

Examples:

- Tests pass.
- Constitution rules are satisfied.
- Existing functionality is preserved.
- Documentation updated where required.

---

# Required Validation

Before completing the task, the agent MUST:

- run automated tests;
- perform a self-review using CODE_REVIEW_CHECKLIST.md;
- verify compliance with ENGINEERING_CONSTITUTION.md;
- update documentation if architecture changed.

---

# Completion State

The task MUST end with exactly one explicit disposition:

- Done
- Blocked
- Needs Review
- Delegated

The task must never finish without a final disposition.

---

# Required Report

The completion report MUST contain:

## Summary

## Files Changed

## Tests Executed

## Constitution Rules Verified

## Architectural Decisions

## Known Limitations

## Suggested Next Steps

---

# Git

Create one logical commit.

The commit message must clearly explain:

- what changed;
- why it changed.

---

# Out of Scope

Explicitly list what was intentionally NOT implemented.

Avoid hidden scope expansion.