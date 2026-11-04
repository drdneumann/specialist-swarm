"""
Upload the Accenture Voice skill and attach it to the coordinator agent.

Run after create_coordinator.py.

Usage:
    python upload_voice_skill.py
"""

import os
from pathlib import Path

from anthropic import Anthropic
from anthropic.lib import files_from_dir


SKILL_DIR = Path("skills/accenture-voice")
DISPLAY_NAME = "Accenture Voice"


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

    # Check if skill already exists
    print("Checking for existing voice skill...")
    skill_id = None
    for page in client.beta.skills.list(source="custom"):
        if page.display_name == DISPLAY_NAME:
            skill_id = page.id
            print(f"Reusing existing skill: {skill_id}")
            break

    if not skill_id:
        print(f"Uploading {DISPLAY_NAME} skill...")
        skill = client.beta.skills.create(
            display_name=DISPLAY_NAME,
            files=files_from_dir(str(SKILL_DIR)),
        )
        skill_id = skill.id
        print(f"  -> {skill_id}")

    # Attach to coordinator
    print(f"Attaching to coordinator ({coordinator_id})...")
    current = client.beta.agents.retrieve(coordinator_id)
    already_attached = any(
        s.get("skill_id") == skill_id for s in (current.skills or [])
    )
    if already_attached:
        print("  Already attached ✓")
    else:
        new_skills = list(current.skills or []) + [
            {"type": "custom", "skill_id": skill_id, "version": "latest"}
        ]
        client.beta.agents.update(
            coordinator_id,
            version=current.version,
            skills=new_skills,
        )
        print("  Attached ✓")

    print(f"\nDone. Next: python run_deal_desk.py")


if __name__ == "__main__":
    main()
