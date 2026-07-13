# Engineering Constitution v1.0

This Constitution defines mandatory engineering rules for all contributors, human and AI.

These rules override implementation convenience.

---

# Architecture

### R-001

Presentation → Services → Domain → Repositories → Infrastructure

Dependencies must never point upward.

---

### R-002

Business logic belongs only in Services.

---

### R-003

Presentation never accesses Repositories directly.

---

# Domain

### R-004

Domain models are strongly typed.

Do not expose `dict` as a public interface.

---

### R-005

Domain models must not depend on:

- SQLite
- JSON
- HTTP
- GUI
- CLI

---

### R-006

Domain models contain business concepts only.

---

# Persistence

### R-007

Repositories perform persistence only.

No business logic.

---

### R-008

Repositories never own transactions.

Never call:

- commit()
- rollback()

---

### R-009

Repositories map storage objects to Domain models.

---

# Services

### R-010

Services coordinate business workflows.

---

### R-011

Services own transaction boundaries.

---

### R-012

Services orchestrate multiple repositories.

---

# Typing

### R-013

Public APIs must be strongly typed.

Avoid `Any`.

Avoid `dict[str, Any]`.

---

### R-014

Prefer:

- dataclasses
- enums
- typed collections

---

# Code Quality

### R-015

One function.

One responsibility.

---

### R-016

One class.

One responsibility.

---

### R-017

Duplicate business logic is forbidden.

Extract shared abstractions.

---

# Errors

### R-018

Never silently ignore exceptions.

---

### R-019

Never expose secrets.

---

# Testing

### R-020

Every behavior change requires tests.

---

# Documentation

### R-021

Architecture changes require documentation updates.

---

# Git

### R-022

One logical change per commit.

---

# Definition of Done

A task is complete only if:

- Architecture complies with this Constitution.
- Tests pass.
- Documentation is updated.
- No intentional technical debt was introduced.
- Changes are committed.