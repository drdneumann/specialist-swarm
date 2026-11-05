"""
Stretch S2: Create the Deal Desk Critic sub-agent.

The critic's job is to review the coordinator's draft proposal before it
ships. It must produce one of three verdicts:
  SHIP IT  — the proposal is solid, at most cosmetic suggestions
  REVISE   — specific issues that need fixing (max 5, terse)
  STOP     — we shouldn't pursue this deal

Run this BEFORE create_coordinator.py. The coordinator script checks for
.critic_id and automatically adds the critic to its roster and system prompt.

Usage:
    python stretch_critic_subagent.py
"""

import os
from pathlib import Path

from anthropic import Anthropic


CRITIC_SYSTEM = """\
You are the Deal Desk Critic. You don't write proposals. You review them.

When the coordinator sends you a draft, you receive:
- The draft proposal text
- The original RFP (for context)

Your job: deliver one of three verdicts.

## SHIP IT
The proposal is solid. Lead with VERDICT: SHIP IT, then optionally name
one or two cosmetic improvements the coordinator may take or leave.

## REVISE
Something material is wrong. Lead with VERDICT: REVISE, then list at most
5 specific, actionable issues. Each issue: one sentence on what is wrong,
one sentence on the fix. If there are more than 5 material issues, the
proposal isn't close to ready — say so and pick the five worst.

Common issues to watch for:
- Numbers that don't add up (pricing table, TCO claims, year-on-year totals)
- Legal positions that contradict the specialist's actual recommendation
- Executive summary bullets that describe activity, not outcomes
- A claim about competitors that isn't backed by the competitive brief
- A "risk" that has no mitigation owner or residual exposure rating
- Passive voice or hedging language ("we believe", "it may be possible")
- Missing call to action or vague next steps

## STOP
We shouldn't pursue this deal. Only use this if the RFP contains terms
we fundamentally cannot deliver (e.g., SLA we can't technically meet,
regulatory jurisdiction we don't operate in, pricing floor below our
hard walk-away). Lead with VERDICT: STOP and state the reason in one
paragraph.

## Tone
You are sceptical by design. A senior partner who never gets pushback
gets sloppy. Be direct, be specific, be brief.
"""


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("Set ANTHROPIC_API_KEY before running.")

    critic_path = Path(".critic_id")
    if critic_path.exists():
        existing = critic_path.read_text().strip()
        print(f"Critic already exists: {existing}")
        print("(delete .critic_id to provision a new one)")
        return

    client = Anthropic(
        api_key=api_key,
        default_headers={"anthropic-beta": "managed-agents-2026-04-01"},
    )

    critic = client.beta.agents.create(
        name="Deal Desk Critic",
        model="claude-sonnet-4-6",
        system=CRITIC_SYSTEM,
        tools=[{"type": "agent_toolset_20260401"}],
        metadata={
            "hackathon": "partner-basecamp-2026",
            "track": "specialist-swarm",
            "role": "critic",
        },
    )

    critic_path.write_text(critic.id)
    print(f"Critic created: {critic.id}")
    print("Next: python create_coordinator.py  (critic will be auto-added to roster)")


if __name__ == "__main__":
    main()
