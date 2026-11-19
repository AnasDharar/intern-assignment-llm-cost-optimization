from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from question2.agent import SupportPipeline


def print_ticket_breakdown(ticket_id: str, label: str) -> None:
    pipe = SupportPipeline()
    pipe.handle_ticket(ticket_id)

    call = pipe.session.calls[0]
    print(f"=== Question 2 Breakdown: {ticket_id} ({label}) ===")
    print(f"Input tokens:        {call.input_tokens} (pts: {call.input_tokens * 3})")
    print(f"Output tokens:       {call.output_tokens} (pts: {call.output_tokens * 15})")
    print(f"Total points:        {call.points()}\n")


def main() -> None:
    print_ticket_breakdown("T-1001", "Physical Fulfillment Path")
    print_ticket_breakdown("T-1002", "Denial / Policy Send Path")


if __name__ == "__main__":
    main()
