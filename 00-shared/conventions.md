# Conventions

Rules that apply to every workspace in Council, regardless of which folder it's working in. The agent (Claude) reads this once per task, alongside the workspace's own `CONTEXT.md` — it does not get restated per-workspace.

## Comments

only on non-obvious WHY, never on WHAT.

## Code style

{Fill in: formatting, naming, language/framework defaults, anything you find yourself repeating across workspaces.}

## Writing style

- README files: always short and concise. 

## Anything else that's true everywhere

- Workspace output (sites, mockups, applications, state, renders) goes in a gitignored folder or outside the repo. Only code, templates, config structure and docs are committed, so using a workspace never creates a commit.
