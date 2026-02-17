# Off The Rails

Browser RPG (MVPQuest) — vanilla JS + Canvas, no external dependencies, deployed via GitHub Pages.

## Tech stack

- **Language:** Vanilla JavaScript + Canvas API
- **Hosting:** GitHub Pages from `main` branch
- **Tests:** None yet

## Operations

- **GitHub repo:** `scarolan/off-the-rails`
- **GitHub Project board:** #4 (`gh project item-add 4 --owner scarolan --url <issue-url>`)
- **Filing issues:** "Put it in the backlog" means all three steps: (1) `gh issue create` with `bug`/`enhancement` label, (2) `gh project item-add 4 --owner scarolan --url <URL>`, (3) `gh issue edit <URL> --add-label shelly`. CLI-created issues are NOT auto-added to the board — you must do it manually.

## Git Conventions

- One commit per phase/issue

## Shelly automation pipeline

Issues labeled `shelly` flow through the automated pipeline.
See `.github/workflows/shelly-label.yml` for project board sync.
