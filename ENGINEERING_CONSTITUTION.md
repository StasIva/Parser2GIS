# Engineering Constitution v0.1

These rules are mandatory for all implementation tasks.

## Architecture

- Repository classes must never call commit() directly.
- Transaction boundaries belong to the application/service layer.
- CLI and GUI must never access repositories directly.
- Business logic must go through an application service layer.

## Domain Model

- Do not use dict for domain entities.
- Use dataclasses or Pydantic models.
- Public APIs should return typed objects.

## Code

- One responsibility per class.
- Avoid magic constants.
- Prefer composition over large classes.
- Keep modules cohesive.

## Testing

- Preserve existing tests.
- Add tests for every behavior changed during refactoring.

## Goal

Improve architecture without changing observable behavior.