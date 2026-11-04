# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A hackathon demo ("Option 3 — Specialist Swarm"): a Deal Desk built on Claude Managed Agents multi-agent (research preview, beta header `managed-agents-2026-04-01`). One coordinator agent fans an RFP out to four specialist sub-agents in parallel, then synthesises a branded Word proposal. There is no build, lint, or test tooling — only standalone Python scripts that call the Anthropic API.

## Commands

```bash
pip install -r requirements.txt          # anthropic, python-dotenv
export ANTHROPIC_API_KEY="sk-ant-..."    # required by every script (PowerShell: $env:ANTHROPIC_API_KEY="...")

python setup_environment.py              # once: cloud Environment -> .environment_id
python create_specialists.py             # -> .specialist_ids.json
python upload_skills.py                  # -> .skill_ids.json, attaches skills to specialists
python create_coordinator.py             # -> .coordinator_id
python run_deal_desk.py                  # streams events, writes outputs/
python download_deliverable.py [sesn_…]  # re-fetch files for last (or given) session
```

Run order matters and the README is inconsistent with the code: `run_deal_desk.py` requires `.environment_id` (README never mentions `setup_environment.py`), and its error message gives the order specialists → skills → coordinator. Use that order.

## Architecture

- **State lives in dotfiles in the repo root**, written by one script and read by the next: `.environment_id`, `.specialist_ids.json`, `.coordinator_id`, `.skill_ids.json`, `.last_session_id`. Deleting one forces re-provisioning; `create_*` scripts are **not** idempotent (they create new agents each run), while `setup_environment.py` and `upload_skills.py` are (reuse by existing file / display title).
- **Specialists** (`create_specialists.py`): the `SPECIALISTS` list holds system prompts and models (Pricing/Legal/Technical Fit on Sonnet, Competitive on Haiku). All use the `agent_toolset_20260401` toolset.
- **Coordinator** (`create_coordinator.py`): Opus, `multiagent={"type": "coordinator", "agents": [...]}` built from `.specialist_ids.json`. The system prompt hardcodes the roster names, so renaming a specialist requires updating `COORDINATOR_SYSTEM` too.
- **Skills** (`skills/<name>/SKILL.md`, YAML frontmatter with `name` + `description`): uploaded via Skills API, attached to specialists via `agents.update(version=current.version, ...)`. The `SKILL_TO_SPECIALIST` map in `upload_skills.py` is the wiring. Technical Fit has no skill — it relies on `product-overview.md` passed in context. The coordinator references a "BTS branding skill" / docx skill that is not uploaded by any script here.
- **Run** (`run_deal_desk.py`): inlines the RFP, `past-wins.json`, and `product-overview.md` from `synthetic-data/` into a single user message (no Files API), streams session events (`session.thread_created`, `agent.thread_message_*`, …) until `session.status_idle`, then downloads all session-scoped files to `outputs/` under their original filenames (the README's `outputs/proposal-response.docx` is not a guaranteed name).
- `stretch_critic_subagent.py`, `stretch-goals.md`, `scenario-cards.md` are optional extensions (critic agent, alternate rosters).

## Team workflow (three people, shared repo)

- The dotfiles listed above and `outputs/` are per-person and gitignored. Never commit them; each person runs the setup scripts themselves and gets their own agent IDs.
- If the team shares one workspace, every `create_*` run adds duplicate agents. Tell teammates before re-running them.
- `upload_skills.py` reuses an existing skill by display title, so edits to a `SKILL.md` are not pushed once the skill exists in the workspace. Delete the skill in the Console or upload a new version to publish changes.
