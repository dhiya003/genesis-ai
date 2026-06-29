"""Approval gates for manual Genesis department transitions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from apps.storage import JsonStore

APPROVAL_MODES = {"auto", "manual", "human"}


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


@dataclass(frozen=True)
class ApprovalManager:
    """Creates and resolves approval gates before downstream departments run."""

    store: JsonStore

    def request(self, project_id: str, workflow_id: str, gate: str, mode: str = "auto", requested_by: str = "genesis") -> dict[str, Any]:
        normalized_mode = mode.strip().lower()
        if normalized_mode not in APPROVAL_MODES:
            raise ValueError(f"approval mode must be one of: {', '.join(sorted(APPROVAL_MODES))}")
        now = _now_iso()
        approval = {
            "id": str(uuid4()),
            "projectId": project_id,
            "workflowId": workflow_id,
            "gate": gate,
            "mode": normalized_mode,
            "status": "APPROVED" if normalized_mode == "auto" else "PENDING",
            "requestedBy": requested_by,
            "requestedAt": now,
            "updatedAt": now,
            "decision": None,
        }
        if normalized_mode == "auto":
            approval["decision"] = {"actor": "system", "note": "Auto-approved by runtime mode.", "decidedAt": now}
        self.store.save_approval(approval)
        return approval

    def approve(self, approval_id: str, actor: str = "founder", note: str | None = None) -> dict[str, Any]:
        return self._decide(approval_id, "APPROVED", actor, note)

    def reject(self, approval_id: str, actor: str = "founder", note: str | None = None) -> dict[str, Any]:
        return self._decide(approval_id, "REJECTED", actor, note)

    def _decide(self, approval_id: str, status: str, actor: str, note: str | None) -> dict[str, Any]:
        approval = self.store.get_approval(approval_id)
        if approval["status"] != "PENDING":
            raise ValueError("Only PENDING approvals can be decided")
        now = _now_iso()
        approval["status"] = status
        approval["updatedAt"] = now
        approval["decision"] = {"actor": actor, "note": note or "", "decidedAt": now}
        self.store.save_approval(approval)
        return approval
