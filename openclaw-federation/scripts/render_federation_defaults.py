#!/usr/bin/env python3
import argparse
import json
from dataclasses import dataclass, asdict
from typing import List


@dataclass
class BotConfig:
    bot_id: str
    machine: str
    role: str
    capabilities: List[str]
    presence_key: str


def infer_role(machine: str) -> str:
    lowered = machine.lower()
    if 'vm' in lowered or 'lab' in lowered:
        return 'lab'
    if 'nas' in lowered or 'host' in lowered:
        return 'ops'
    if 'cloud' in lowered or 'server' in lowered or 'vps' in lowered:
        return 'coordinator'
    return 'coordinator'


def infer_capabilities(role: str) -> List[str]:
    defaults = {
        'coordinator': ['route', 'summarize', 'delegate'],
        'ops': ['docker', 'storage', 'files', 'services'],
        'lab': ['browser', 'code', 'scrape', 'experiments'],
    }
    return defaults[role]


def slugify(value: str) -> str:
    return value.lower().replace('_', '-').replace(' ', '-')


def main() -> None:
    parser = argparse.ArgumentParser(description='Render starter config for an OpenClaw federation.')
    parser.add_argument('--machines', nargs='+', required=True, help='Machine names, e.g. cloud nas-host nas-vm')
    parser.add_argument('--chat-id', required=True, help='Shared Telegram chat id')
    args = parser.parse_args()

    bots = []
    for machine in args.machines:
        role = infer_role(machine)
        bot_id = f"{slugify(machine)}-bot"
        bots.append(BotConfig(
            bot_id=bot_id,
            machine=machine,
            role=role,
            capabilities=infer_capabilities(role),
            presence_key=f"claw:presence:{bot_id}",
        ))

    rendered = {
        'telegram': {'chat_id': args.chat_id},
        'redis': {
            'task_stream': 'claw:tasks',
            'result_stream': 'claw:results',
            'error_stream': 'claw:errors',
            'presence_prefix': 'claw:presence:'
        },
        'bots': [asdict(bot) for bot in bots],
    }
    print(json.dumps(rendered, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
