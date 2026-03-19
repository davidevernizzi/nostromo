# Nostromo – Claude Code Guidelines

## Development Workflow

Every development effort — whether a new feature or a significant change — **must begin with a specification file** in `docs/iterations/` before any code is written.

### Iteration vs. Bugfix

| Type | Action |
|---|---|
| New feature | Create a new iteration file in `docs/iterations/` |
| Bugfix | Update the relevant existing iteration file |

---

## Iteration File Format

Each file in `docs/iterations/` must follow this structure:

```markdown
# <iteration-id> – <Human Readable Short Description>

## Description
A concise, human-readable summary of the feature or change and its purpose.

## Specification
Agent-oriented, detailed specification of what must be built or changed.
Include: inputs, outputs, data models, API contracts, edge cases, constraints.
This section is the source of truth for implementing agents.

## Tasks

Each task entry follows this format:

### T<n>: <Task Title>
- **Agent**: frontend | backend | infrastructure | general
- **Depends on**: T<x>, T<y> | none (can run in parallel)
- **Description**: What the task entails.
```

### Iteration ID Convention

Use a zero-padded sequential integer: `0001`, `0002`, etc.
File names: `docs/iterations/0001-short-description.md`

---

## Principles

- No code without a spec. If it's not in an iteration, it shouldn't be built.
- Tasks that have no dependencies should be highlighted as parallelizable.
- Assign tasks to agents when the domain is clear (frontend, backend, infrastructure).
- Keep specs up to date — if the implementation diverges, update the spec.
