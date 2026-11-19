from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from question1.agent import SupportCopilot


def main() -> None:
    ticket_id = "T-1001"
    copilot = SupportCopilot()
    copilot.handle_ticket(ticket_id)

    call = copilot.session.calls[0]
    uncached_tokens = call.input_tokens - min(call.cached_prefix_tokens, call.input_tokens)

    print(f"=== Question 1 Cost Breakdown ({ticket_id}) ===")
    print(f"Input tokens:        {call.input_tokens} (pts: {uncached_tokens * 3})")
    print(f"Cached prefix:       {call.cached_prefix_tokens} (pts: {int(call.cached_prefix_tokens * 0.3)})")
    print(f"Output tokens:       {call.output_tokens} (pts: {call.output_tokens * 15})")
    print(f"Total points:        {call.points()}")


if __name__ == "__main__":
    main()
