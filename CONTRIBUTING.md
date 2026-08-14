# Git Commit Convention for AI Agents

**Target Audience:** All AI Coding Agents and Human Developers working on this repository.

## Core Rules

1. **Language:** All commit messages MUST be written in **English**. No exceptions.
2. **Format:** You MUST follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.
3. **Structure:** `<type>[optional scope]: <description>`
4. **CI Skipping:** Commits that do not affect the pipeline's production logic (e.g., changes to TODO files, documentation, or other non-code files) MUST include the `[skip ci]` tag in the commit message to prevent unnecessary CI pipeline runs.

## Allowed Commit Types (Tags)

* **`feat:`** – A new feature or functionality (e.g., `feat: add matches data extraction from API-Football`).
* **`fix:`** – A bug fix (e.g., `fix: resolve rate limit handling in requests`).
* **`chore:`** – Maintenance tasks, project setup, dependency updates. Code changes that do not affect production logic (e.g., `chore: setup project folder structure and python virtual environment`).
* **`refactor:`** – Code changes that neither fix a bug nor add a feature, but improve code structure (e.g., `refactor: extract s3 upload logic to a separate function`).
* **`docs:`** – Documentation changes only (e.g., `docs: update setup instructions in README`).
* **`style:`** – Formatting, missing semi-colons, whitespace, etc. No logic changes.
* **`test:`** – Adding or modifying tests.

## Description Guidelines

* Write in the **imperative, present tense**: use "add" not "added" or "adds", use "fix" not "fixed".
* Do not capitalize the first letter of the description.
* Do not place a period (`.`) at the end of the description.

## Examples

* `chore: initialize ingest directory structure and .env template`
* `feat(terraform): configure aws s3 bucket and iam user`
* `fix(api): correct json parsing logic for teams endpoint`
* `docs: update TODO with databricks transformation task [skip ci]`