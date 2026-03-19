# Nostromo – Claude Code Guidelines

## Development Workflow

Development is split into **two phases**, each run as a separate Claude command:

1. **Spec phase** — Write the iteration specs in `docs/iterations/`. No code is written.
2. **Implementation phase** — Implement the tasks defined in the iteration specs.

Every development effort — whether a new feature or a significant change — **must begin with the spec phase** before any code is written.

### Iteration vs. Bugfix

| Type | Action |
|---|---|
| New feature | Create a new iteration directory in `docs/iterations/` |
| Bugfix | Update the relevant existing iteration files |

---

## Iteration Directory Structure

Each iteration lives in its own subdirectory:

```
docs/iterations/<id>_<short-description>/
  humans.md          ← human-readable description and rationale
  agents.md          ← agent-oriented specification (source of truth for implementors)
  task001_<short-description>.md
  task002_<short-description>.md
  ...
```

### `humans.md`

```markdown
# <id> – <Human Readable Short Description>

## Description
A concise, human-readable summary of the feature or change and its purpose.

## Rationale
Why this change is needed. Context, motivation, constraints.
```

### `agents.md`

```markdown
# <id> – Specification

## Overview
One-paragraph summary for the implementing agent.

## Inputs / Outputs
...

## Data Models
...

## API Contracts
...

## Edge Cases & Constraints
...
```

### `task<n>_<short-description>.md`

```markdown
# Task <n>: <Task Title>

- **Agent**: frontend | backend | infrastructure | general
- **Depends on**: task<x>, task<y> | none (can run in parallel)

## Description
What the task entails.

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
```

### Iteration ID Convention

Use a zero-padded sequential integer: `0001`, `0002`, etc.
Directory names: `docs/iterations/0001_short-description/`
Task file names: `task001_short-description.md`, `task002_short-description.md`

---

## Principles

- No code without a spec. If it's not in an iteration, it shouldn't be built.
- The spec phase and implementation phase are separate Claude commands — do not mix them.
- Tasks that have no dependencies should be highlighted as parallelizable.
- Assign tasks to agents when the domain is clear (frontend, backend, infrastructure).
- Keep specs up to date — if the implementation diverges, update the spec.
