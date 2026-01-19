import json
from stackfix.agent import _parse_agent_response

cases = [
    '{"summary":"ok","confidence":0.5,"patch_unified_diff":"","rerun_command":["pytest","-q"]}',
    '{"summary":"ok","confidence":"0.8","patch_unified_diff":null,"rerun_command":"pytest -q"}',
    '{"summary":"ok"}',
    'plain text response',
]

for i, content in enumerate(cases, 1):
    result = _parse_agent_response(content)
    print(f"case {i}: summary={result.get('summary')!r} rerun={result.get('rerun_command')} warning={result.get('_warning')}")
