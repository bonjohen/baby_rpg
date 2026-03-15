# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Baby RPG — a role-playing game project. Repository is currently in its initial state with no source code yet.

## CRITICAL: Plan Before Implementing

- **ALWAYS create a plan document before doing any implementation work.** When the user asks you to build, fix, refactor, or implement something, write a plan document in `docs/` first (e.g., `docs/feature_name_plan.md`) and present it for review.
- **Do NOT start writing code until the user has reviewed and approved the plan.**
- Plan documents should include: goals, affected files, step-by-step approach, and any open questions.
- Small, obvious fixes (typos, one-line changes) are exempt — use judgment.

- **NEVER use an Anthropic API key.** Do not import, configure, or wire `AnthropicAdapter` or any direct API key-based adapter.

## jcodemunch MCP Integration

This project has a **jcodemunch MCP server** configured for code intelligence. Use jcodemunch tools for codebase exploration, symbol lookup, and code search — they provide AST-aware results that are faster and more structured than raw file reads.

- **Repo identifier**: `bonjohen/baby_rpg` (use this for all `repo` parameters)
- **Index**: Run `index_repo(url: "bonjohen/baby_rpg", use_ai_summaries: false)` to index/re-index. Use `incremental: true` (default) after code changes.
- **AI summaries are disabled** (`use_ai_summaries: false`) — summaries use docstring/signature fallback only. Do not enable AI summaries (they require API keys we don't use).

### Available Tools

| Tool | Use When |
|------|----------|
| `list_repos` | Check what repos are indexed |
| `index_repo` / `index_folder` | Index or re-index the codebase |
| `invalidate_cache` | Force full re-index (deletes cached index) |
| `get_repo_outline` | Quick overview: directories, languages, symbol counts |
| `get_file_tree` | Browse file structure, optionally filtered by path prefix |
| `get_file_outline` | List all symbols in a file (functions, classes, types) with signatures |
| `get_file_content` | Read cached source, optionally sliced to line range |
| `get_symbol` | Get full source of a specific symbol by ID |
| `get_symbols` | Batch-retrieve multiple symbols at once |
| `search_symbols` | Search by name/signature/summary; filter by kind (`function`, `class`, `type`, etc.) or language |
| `search_text` | Full-text search across file contents (strings, comments, config values) |

### When to Use jcodemunch vs Built-in Tools

- **Use jcodemunch** for: understanding code structure, finding symbol definitions, exploring unfamiliar parts of the codebase, getting file outlines before diving in
- **Use built-in Read/Glob/Grep** for: reading specific known files, making edits, simple pattern matching
- **Prefer `search_symbols`** over Grep when looking for function/class/type definitions
- **Prefer `get_file_outline`** before reading a large file to understand its structure first

## CRITICAL: Always Leave Services Running

- **After ANY code change, always restart and leave the dev server running.** Run `cd /c/Projects/story_v5/app && npm run dev` in the background before finishing.
- The Vite dev server auto-starts the bridge server — no separate command needed.
- **Never finish work without confirming the app is accessible in the browser.**
- Use `run_in_background` for long-running services so they persist.

## Project Overview

## Repository Structure

```
docs/                              ← Active planning and specs


## Goal Status

## Key Conventions

### Workflow Rules

### Task Tracking

Tasks use checkbox syntax:
- `[ ]` — pending
- `[~]` — actively in progress (Typically, only ONE task at a time)
- `[X]` — complete

- Commit at each phase end
- Echo banners for task/phase transitions
- Don't stop between phases — continue to the next
- At the completion of all phases, push.
- Only mark the single active task as `[~]`
- Do not prefix bash commands with `cd /c/Projects/baby_rpg` — the working directory is already set to the project root

### Deployment

- TBD

### Bug Tracking

- TBD

### Quality Standards

- TBD