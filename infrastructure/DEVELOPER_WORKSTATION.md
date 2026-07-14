# Developer Workstation

## Purpose

This document describes the complete engineering workstation required to
develop Parser2GIS and future AI-assisted projects.

It is intentionally separate from the Engineering System.

Engineering documents describe **how we work**.

This document describes **where we work**.

---

# Goals

The workstation must be:

- reproducible
- recoverable
- replaceable
- easy to migrate

A complete workstation rebuild should be possible within one working day.

---

# Host Machine

Document after installation.

Example:

CPU:

RAM:

Storage:

OS:

---

# Operating System

Ubuntu

Version:

Kernel:

---

# Installed Software

## Git

Version:

Configuration location:

~/.gitconfig

---

## Python

Version:

Installation method:

---

## Node.js

Version:

Installation method:

---

## npm

Version:

---

## Paperclip

Version:

Installation method:

Configuration:

~/.paperclip

---

## OpenCode

Version:

Installation method:

---

## VS Code

Version:

Extensions:

- Continue

---

# Environment Variables

Document every required variable.

Never store secrets inside this document.

Example

PAPERCLIP_API_KEY

OPENAI_API_KEY

OPENROUTER_API_KEY

...

---

# SSH

Keys

Known hosts

GitHub authentication

---

# Project Layout

Example

~/projects

    parser2gis/

    paperclip/

---

# Python Environment

Every project owns its own virtual environment.

Example

parser2gis/

    .venv/

Virtual environments are never backed up.

They are recreated.

---

# Node Environment

node_modules

must never be backed up.

Always rebuild.

---

# Files To Preserve

Mandatory backup

~/.paperclip

~/.gitconfig

~/.ssh

Projects

.env

---

# Files NOT To Preserve

.venv

node_modules

dist

build

__pycache__

.pytest_cache

coverage

---

# Migration Procedure

1. Install OS

2. Install Git

3. Install Python

4. Install Node

5. Clone repositories

6. Restore SSH

7. Restore Git config

8. Restore Paperclip

9. Install Python dependencies

10. Install Node dependencies

11. Verify builds

12. Run tests

---

# Validation Checklist

Git

□ OK

Python

□ OK

Paperclip

□ OK

OpenCode

□ OK

Parser2GIS

□ Builds

Parser2GIS

□ Tests pass

Parser2GIS

□ GUI starts

---

# Backup Strategy

Regular backup required

- repositories
- ~/.paperclip
- ~/.ssh
- ~/.gitconfig
- .env

Never back up build artifacts.

---

# Recovery Procedure

Clone repositories.

Restore configuration.

Recreate environments.

Run tests.

Verify Paperclip.

Verify OpenCode.

---

# Change Log

Infrastructure changes should be recorded here.

This document evolves independently from the Engineering System.