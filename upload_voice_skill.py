"""
Upload the coordinator-level skills (Accenture Voice, HTML Slide Proposal)
and attach them to the coordinator agent.

Run after create_coordinator.py.

Usage:
    python upload_voice_skill.py
"""

import os
from pathlib import Path

from anthropic import Anthropic
from anthropic.lib import files_from_dir


COORDINATOR_SKILLS = [
    ("skills/accenture-voice", "Accenture Voice"),
    ("skills/html-slide-proposal", "Html Slide Proposal"),
]


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("Set ANTHROPIC_API_KEY before running.")

    coordinator_path = Path(".coordinator_id")
    if not coordinator_path.exists():
        raise SystemExit("Run create_coordinator.py first.")
    coordinator_id = coordinator_path.read_text().strip()

    client = Anthropic(
        default_headers={"anthropic-beta": "managed-agents-2026-04-01"},
    )

    print("Checking for existing skills...")
    existing = {s.display_name: s.id for s in client.beta.skills.list(source="custom")}

    for skill_dir, display_name in COORDINATOR_SKILLS:
        if display_name in existing:
            skill_id = existing[display_name]
            print(f"Reusing existing skill: {display_name} ({skill_id})")
        else:
            print(f"Uploading {display_name}...")
            skill = client.beta.skills.create(
                display_name=display_name,
                files=files_from_dir(skill_dir),
            )
            skill_id = skill.id
            print(f"  -> {skill_id}")

        current = client.beta.agents.retrieve(coordinator_id)
        attached = [s.model_dump(exclude_none=True) for s in (current.skills or [])]
        if any(s.get("skill_id") == skill_id for s in attached):
            print("  already attached")
            continue
        client.beta.agents.update(
            coordinator_id,
            version=current.version,
            skills=attached
            + [{"type": "custom", "skill_id": skill_id, "version": "latest"}],
        )
        print(f"  attached to coordinator ({coordinator_id})")

    print("\nDone. Next: python run_deal_desk.py")


if __name__ == "__main__":
    main()
