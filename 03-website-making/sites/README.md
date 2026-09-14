# sites

Each website project gets its own subfolder here (`sites/{slug}/`), self-contained like any other workspace's product folder. When starting one, pull what you need from `../assets/` rather than duplicating brand files inside the site folder unless the build process requires a local copy — if it does, treat `assets/` as the source of truth and the copy as generated.

**Mockup before backend.** Every new site starts in `sites/{slug}/mockups/` — a few design approaches, front-end only, no data/auth/API wiring — until one is explicitly approved. Only then does real, functional build work start in `sites/{slug}/`. See the parent `../CONTEXT.md` Process section for how the mockup gets made.
