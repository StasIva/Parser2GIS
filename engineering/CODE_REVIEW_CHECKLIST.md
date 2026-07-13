# Code Review Checklist

Every code review should verify the following rules.

---

# Architecture

- [ ] R-001 Layering is respected.
- [ ] R-002 Business logic exists only in Services.
- [ ] R-003 Presentation never accesses Repositories directly.

---

# Domain

- [ ] R-004 Domain models expose typed APIs.
- [ ] R-005 Domain has no infrastructure dependencies.
- [ ] R-006 Domain contains business concepts only.

---

# Persistence

- [ ] R-007 Repositories contain persistence only.
- [ ] R-008 No commit()/rollback() inside repositories.
- [ ] R-009 Repositories return Domain models.

---

# Services

- [ ] R-010 Business workflows are implemented in Services.
- [ ] R-011 Services own transactions.
- [ ] R-012 Services coordinate repositories.

---

# Typing

- [ ] R-013 Public APIs are strongly typed.
- [ ] R-014 Prefer dataclasses, enums and typed collections.

---

# Code Quality

- [ ] R-015 Functions have one responsibility.
- [ ] R-016 Classes have one responsibility.
- [ ] R-017 No duplicated business logic.

---

# Reliability

- [ ] R-018 Exceptions are handled appropriately.
- [ ] R-019 No secrets are committed or logged.

---

# Testing

- [ ] R-020 Tests cover the new behaviour.

---

# Documentation

- [ ] R-021 Documentation updated if architecture changed.

---

# Git

- [ ] R-022 Commit history remains clean.