#!/usr/bin/env python3
import argparse
import json
import sys
from typing import Any, Dict, List


COMMON_REQUIRED = ['type']
TASK_REQUIRED = ['task_id', 'origin_bot', 'assigned_by', 'hop_count', 'ttl', 'request']
RESULT_REQUIRED = ['task_id', 'origin_bot', 'return_to', 'status', 'summary']
HEARTBEAT_REQUIRED = ['bot_id', 'role', 'capabilities', 'busy', 'health', 'last_seen']


class ValidationError(Exception):
    pass


def require_fields(data: Dict[str, Any], fields: List[str]) -> None:
    missing = [field for field in fields if field not in data]
    if missing:
        raise ValidationError(f"missing fields: {', '.join(missing)}")


def validate_ttl_and_hops(data: Dict[str, Any]) -> None:
    if 'ttl' in data and (not isinstance(data['ttl'], int) or data['ttl'] < 0):
        raise ValidationError('ttl must be a non-negative integer')
    if 'hop_count' in data and (not isinstance(data['hop_count'], int) or data['hop_count'] < 0):
        raise ValidationError('hop_count must be a non-negative integer')


def validate_task(data: Dict[str, Any]) -> None:
    require_fields(data, TASK_REQUIRED)
    validate_ttl_and_hops(data)
    if not isinstance(data['request'], dict):
        raise ValidationError('request must be an object')


def validate_result(data: Dict[str, Any]) -> None:
    require_fields(data, RESULT_REQUIRED)


def validate_heartbeat(data: Dict[str, Any]) -> None:
    require_fields(data, HEARTBEAT_REQUIRED)
    if not isinstance(data['capabilities'], list):
        raise ValidationError('capabilities must be a list')


def main() -> None:
    parser = argparse.ArgumentParser(description='Validate OpenClaw federation envelopes.')
    parser.add_argument('path', help='Path to a JSON file containing one envelope')
    args = parser.parse_args()

    with open(args.path, 'r', encoding='utf-8') as handle:
        data = json.load(handle)

    require_fields(data, COMMON_REQUIRED)
    envelope_type = data['type']

    if envelope_type == 'task':
        validate_task(data)
    elif envelope_type == 'result':
        validate_result(data)
    elif envelope_type == 'heartbeat':
        validate_heartbeat(data)
    else:
        raise ValidationError(f'unsupported envelope type: {envelope_type}')

    print('OK')


if __name__ == '__main__':
    try:
        main()
    except ValidationError as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(1)
