from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

from agent.state import draft_state


class PatchEngineError(Exception):
    """Base error for deterministic patch failures."""


class PatchValidationError(PatchEngineError):
    """Raised when a repair instruction is malformed or unsafe."""


class PatchMatchError(PatchEngineError):
    """Raised when expected repair text is missing or ambiguous."""


@dataclass(frozen=True)
class PatchApplication:
    issue_id: str
    block_id: str
    action: str
    char_start: int
    char_end: int
    old_length: int
    new_length: int


@dataclass(frozen=True)
class PatchReport:
    original_length: int
    final_length: int
    patch_count: int
    applications: list[PatchApplication]

    def to_dict(self) -> dict[str, Any]:
        return {
            "original_length": self.original_length,
            "final_length": self.final_length,
            "patch_count": self.patch_count,
            "applications": [asdict(item) for item in self.applications],
        }


def _validate_patch(patch: dict[str, Any], index: int) -> None:
    required = ("issue_id", "block_id", "current_text", "action", "replacement")
    missing = [key for key in required if key not in patch]
    if missing:
        raise PatchValidationError(
            f"Patch #{index + 1} missing required fields: {', '.join(missing)}"
        )

    if not isinstance(patch["issue_id"], str) or not patch["issue_id"].strip():
        raise PatchValidationError(f"Patch #{index + 1}: invalid issue_id")

    if not isinstance(patch["block_id"], str) or not patch["block_id"].strip():
        raise PatchValidationError(f"Patch {patch['issue_id']}: invalid block_id")

    if patch["action"] != "REPLACE":
        raise PatchValidationError(
            f"Patch {patch['issue_id']}: unsupported action {patch['action']!r}; "
            "only 'REPLACE' is allowed"
        )

    if not isinstance(patch["current_text"], str) or not patch["current_text"]:
        raise PatchValidationError(
            f"Patch {patch['issue_id']}: current_text must be non-empty"
        )

    if not isinstance(patch["replacement"], str) or not patch["replacement"]:
        raise PatchValidationError(
            f"Patch {patch['issue_id']}: replacement must be non-empty"
        )


def _collect_spans(
    draft: str,
    patches: list[dict[str, Any]],
) -> list[tuple[int, int, dict[str, Any]]]:
    spans: list[tuple[int, int, dict[str, Any]]] = []
    seen_issue_ids: set[str] = set()

    for index, patch in enumerate(patches):
        _validate_patch(patch, index)

        issue_id = patch["issue_id"]
        if issue_id in seen_issue_ids:
            raise PatchValidationError(f"Duplicate issue_id: {issue_id}")
        seen_issue_ids.add(issue_id)

        current_text = patch["current_text"]
        first = draft.find(current_text)
        if first == -1:
            raise PatchMatchError(
                f"Patch {issue_id} failed: current_text was not found in the draft."
            )

        second = draft.find(current_text, first + len(current_text))
        if second != -1:
            raise PatchMatchError(
                f"Patch {issue_id} failed: current_text occurs more than once in the draft "
                f"(first at {first}, second at {second})."
            )

        end = first + len(current_text)
        spans.append((first, end, patch))

    spans.sort(key=lambda item: item[0])

    previous_end = -1
    previous_issue = None
    for start, end, patch in spans:
        if start < previous_end:
            raise PatchMatchError(
                f"Patch spans overlap: {previous_issue} overlaps {patch['issue_id']}"
            )
        previous_end = end
        previous_issue = patch["issue_id"]

    return spans


def apply_patches(
    draft: str,
    patches: Iterable[dict[str, Any]],
) -> tuple[str, PatchReport]:
    """Apply all exact replacements against the original draft."""
    if not isinstance(draft, str):
        raise PatchValidationError("draft must be a string")

    patch_list = list(patches)
    spans = _collect_spans(draft, patch_list)

    patched = draft
    applications: list[PatchApplication] = []

    # Resolve every location against the original draft first, then patch from
    # the end toward the beginning so character offsets remain valid.
    for start, end, patch in reversed(spans):
        current_text = patch["current_text"]
        replacement = patch["replacement"]

        patched = patched[:start] + replacement + patched[end:]

        applications.append(
            PatchApplication(
                issue_id=patch["issue_id"],
                block_id=patch["block_id"],
                action=patch["action"],
                char_start=start,
                char_end=end,
                old_length=len(current_text),
                new_length=len(replacement),
            )
        )

    applications.reverse()

    return patched, PatchReport(
        original_length=len(draft),
        final_length=len(patched),
        patch_count=len(patch_list),
        applications=applications,
    )


def apply_repair_patches(state: draft_state) -> draft_state:
    """LangGraph node: execute Repair Agent patches and produce final_draft."""

    draft = state.get("draft")
    patches = state.get("repair_patches", [])

    if not isinstance(draft, str):
        raise ValueError("Patch Engine requires state['draft'] to be a string")

    if patches is None:
        patches = []

    if not isinstance(patches, list):
        raise ValueError(
            "Patch Engine requires state['repair_patches'] to be a list"
        )

    final_draft, report = apply_patches(draft, patches)

    return {
        **state,
        "final_draft": final_draft,
        "patch_report": report.to_dict(),
        "status": "draft_patched",
    }
