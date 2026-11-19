from __future__ import annotations
from shared.kb import all_articles_blob

import json
import uuid
from dataclasses import dataclass

from shared.billing import CostSession
from shared.kb import expanded_help_center_blob, title_index
from shared.llm import ChatMessage, LlmClient
from shared.tools import format_thread, get_order, get_ticket

from question1.agent import parse_resolution


@dataclass
class TicketResolution:
    action: str
    kb_article: str


class SupportPipeline:
    """Same product as Question 1 — triage, retrieve, compose, audit."""

    def __init__(self, session: CostSession | None = None):
        self.session = session or CostSession()
        self.llm = LlmClient(self.session)
        # self.help_center = expanded_help_center_blob()

    def handle_ticket(self, ticket_id: str) -> TicketResolution:
        ticket = get_ticket(ticket_id)
        order = get_order(ticket["order_id"])
        thread = format_thread(ticket)
        snapshot = json.dumps(order, indent=2)

        triage = self._triage(ticket_id, thread, snapshot)
        retrieved = self._retrieve(triage, snapshot)
        draft = self._compose(ticket_id, thread, snapshot, triage, retrieved)
        final = self._audit(ticket_id, thread, snapshot, triage, retrieved, draft)
        parsed = parse_resolution(final)
        return TicketResolution(parsed.action, parsed.kb_article)

    def _triage(self, ticket_id: str, thread: str, snapshot: str) -> str:
        text = thread.lower()
        if "license" in text or "digital" in text or "ebook" in text:
            tag = "DIGITAL_LICENSE"
        elif "crack" in text or "damage" in text or "broken" in text or "replace" in text:
            tag = "DAMAGE_REPLACEMENT"
        elif "subscription" in text or "renew" in text:
            tag = "SUBSCRIPTION"
        elif "return" in text or "refund" in text:
            tag = "STANDARD_RETURN"
        else:
            tag = "GENERAL"
        return f"TICKET {ticket_id} | CATEGORY: {tag}"


    def _retrieve(self, triage: str, snapshot: str) -> str:
        # messages = [
        #     ChatMessage(
        #         "system",
        #         "Retrieve node: print full text of the eight most relevant help articles.",
        #     ),
        #     ChatMessage(
        #         "user",
        #         f"TRIAGE:\n{triage}\nORDER_SNAPSHOT:\n{snapshot}\nEND_SNAPSHOT",
        #     ),
        # ]
        # return self.llm.chat("retrieve", messages)
        return all_articles_blob()

    def _compose(
        self,
        ticket_id: str,
        thread: str,
        snapshot: str,
        triage: str,
        retrieved: str,
    ) -> str:
        messages = [
            ChatMessage(
                "system",
                "Compose node: output JSON with action, kb_article, customer_reply.",
            ),
            ChatMessage(
                "user",
                "\n\n".join(
                    [
                        f"TICKET {ticket_id}",
                        f"THREAD:\n{thread}",
                        f"ORDER_SNAPSHOT:\n{snapshot}\nEND_SNAPSHOT",
                        f"TRIAGE:\n{triage}",
                        f"ARTICLES:\n{retrieved}",
                        # f"TRIAGE AGAIN:\n{triage}",
                    ]
                ),
            ),
        ]
        return self.llm.chat("compose", messages)

    def _audit(
        self,
        ticket_id: str,
        thread: str,
        snapshot: str,
        triage: str,
        retrieved: str,
        draft: str,
    ) -> str:
        try:
            parsed = parse_resolution(draft)
            valid_actions = {"REFUND", "REPLACE", "SEND_ARTICLE", "ESCALATE_TIER2"}
            if parsed.action not in valid_actions or not parsed.kb_article:
                raise ValueError("Invalid action or missing kb_article")
            return draft
        except Exception:
            # Fallback safety if the model returned malformed output
            return '{"action": "ESCALATE_TIER2", "kb_article": "returns-within-30-days"}'
