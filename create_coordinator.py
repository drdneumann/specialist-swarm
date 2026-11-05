"""
Create the coordinator agent that orchestrates the specialist swarm.

The coordinator's roster is the four specialists created by create_specialists.py.
The coordinator decides which specialists to consult, in what order, and how to
synthesise their outputs into the final deliverable.

Saves the coordinator's ID to .coordinator_id.

Usage:
    python create_coordinator.py
"""

import json
import os
from pathlib import Path

from anthropic import Anthropic


COORDINATOR_SYSTEM_BASE = """\
You are the Senior Partner running the Deal Desk. An inbound RFP has just
arrived. Your job is to orchestrate the specialists, synthesise their work,
and produce a single branded proposal response document.

# Your roster

You can call these specialists:
- Pricing Specialist: commercial terms recommendation
- Legal Reviewer: contract flags and counter-positions
- Technical Fit Specialist: product capability fit
- Competitive Intel Analyst: who else is in the deal and how to position

# How to run a deal

1. Read the RFP yourself first. Note the customer, scope, and any obvious
   curveballs.

2. Delegate to ALL FOUR specialists in parallel. Each gets:
   - The full RFP text
   - A clear, narrow brief stating what you need from them
   - A deadline ("answer in one message, ~300 words")

3. Synthesise their outputs into a single proposal response. The response
   should cover:
   - Executive summary (3 bullets)
   - Our understanding of the customer's need
   - Why we're the right fit (drawing on Technical Fit + Competitive Intel)
   - Commercial proposal (drawing on Pricing)
   - Contract approach (drawing on Legal)
   - Risks and how we mitigate them

4. Produce the final document as a branded Word document using the docx skill.
   Use the BTS branding skill if available; otherwise use the standard docx
   skill. The deliverable is the docx itself, not a chat message.

# How to talk to specialists

When delegating, be direct: "Pricing Specialist: for this RFP, recommend
terms. Include discount band and red-line concessions. Cite past-wins.json
where relevant."

When you receive a specialist's reply, accept it. Don't second-guess. If
you genuinely disagree, send the specialist a follow-up — but only if it
matters.

# Tone

Senior partner running a real deal. Confident, terse, decisive. You move
fast because the RFP deadline is real.
"""

CRITIC_ADDENDUM = """
# Critic review (mandatory before final document)

Your roster includes a Deal Desk Critic. You MUST consult the Critic before
producing the final document.

Steps:
1. Draft your full proposal text (do not produce the docx yet).
2. Send the draft to the Deal Desk Critic with the original RFP as context.
3. The Critic replies with one of three verdicts:
   - VERDICT: SHIP IT → produce the final document now.
   - VERDICT: REVISE → address each issue the Critic named, then re-submit
     to the Critic. Repeat at most twice. After two revision rounds, produce
     the best version you have and note the outstanding issues.
   - VERDICT: STOP → do NOT produce the document. Report the Critic's
     reasoning to the user verbatim.

The Critic is adversarial by design. Its pushback is a feature. Take every
REVISE seriously — it means something in the draft would embarrass us with
the client.
"""


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("Set ANTHROPIC_API_KEY before running.")

    specialist_ids_path = Path(".specialist_ids.json")
    if not specialist_ids_path.exists():
        raise SystemExit("Run create_specialists.py first.")
    specialist_ids = json.loads(specialist_ids_path.read_text())

    # Include critic in roster if stretch_critic_subagent.py was run first
    critic_id_path = Path(".critic_id")
    with_critic = critic_id_path.exists()
    critic_id = critic_id_path.read_text().strip() if with_critic else None

    system = COORDINATOR_SYSTEM_BASE + (CRITIC_ADDENDUM if with_critic else "")

    roster = [
        {"type": "agent", "id": agent_id}
        for agent_id in specialist_ids.values()
    ]
    if with_critic:
        roster.append({"type": "agent", "id": critic_id})

    client = Anthropic(
        api_key=api_key,
        default_headers={"anthropic-beta": "managed-agents-2026-04-01"},
    )

    coordinator = client.beta.agents.create(
        name="Deal Desk Senior Partner" + (" + Critic" if with_critic else ""),
        model="claude-opus-4-7",
        system=system,
        tools=[{"type": "agent_toolset_20260401"}],
        multiagent={"type": "coordinator", "agents": roster},
        metadata={
            "hackathon": "partner-basecamp-2026",
            "track": "specialist-swarm",
            "role": "coordinator",
            "critic": str(with_critic),
        },
    )

    Path(".coordinator_id").write_text(coordinator.id)
    print(f"Coordinator created: {coordinator.id}")
    roster_keys = list(specialist_ids.keys()) + (["critic"] if with_critic else [])
    print(f"Roster: {roster_keys}")
    if with_critic:
        print("Critic review loop is ACTIVE — coordinator will consult critic before shipping.")
    print(f"\nNext: python upload_skills.py then python run_deal_desk.py")


if __name__ == "__main__":
    main()
