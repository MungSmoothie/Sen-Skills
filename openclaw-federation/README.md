# OpenClaw Federation Skill

Multi-instance OpenClaw federation with Redis coordination and Telegram group collaboration.

## Quick Start

1. Install Redis on a shared machine or NAS
2. Configure all OpenClaw instances to use the same Telegram group
3. Install this skill on each machine
4. Run the federation worker: `python -m scripts.runtime`

## Files

- `SKILL.md` - Main skill documentation
- `agents/` - Agent configuration
- `references/` - Detailed guides
- `scripts/` - Utility scripts
- `skill.yaml` - OpenClaw skill manifest
