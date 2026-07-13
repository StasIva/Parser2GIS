from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ChatGptMessage:
    role: str
    content: str
    model_slug: str | None = None
    create_time: datetime | None = None
    status: str | None = None


@dataclass
class ChatGptConversation:
    conversation_id: str
    title: str
    create_time: datetime | None = None
    update_time: datetime | None = None
    default_model_slug: str | None = None
    messages: list[ChatGptMessage] = field(default_factory=list)
    gizmo_id: str | None = None
    is_archived: bool = False


def _parse_timestamp(ts: float | int | None) -> datetime | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def _walk_linear(mapping: dict[str, Any], current_node: str | None) -> list[dict[str, Any]]:
    if not current_node or current_node not in mapping:
        return []

    path: list[dict[str, Any]] = []
    node_id: str | None = current_node
    while node_id:
        node = mapping.get(node_id)
        if not node:
            break
        msg = node.get("message")
        if msg:
            path.append(msg)
        node_id = node.get("parent")

    path.reverse()
    return path


def _extract_text(msg: dict[str, Any]) -> str:
    content = msg.get("content", {})
    parts = content.get("parts", [])
    texts: list[str] = []
    for part in parts:
        if isinstance(part, str):
            texts.append(part)
        elif isinstance(part, dict):
            if part.get("content_type") == "image_asset" or part.get("content_type") == "image":
                texts.append("[Image]")
            elif "text" in part:
                texts.append(str(part["text"]))
            elif "url" in part:
                texts.append(str(part["url"]))
            else:
                texts.append(json.dumps(part, ensure_ascii=False))
    return "\n".join(texts)


def parse_conversations_json(path: str | Path) -> list[ChatGptConversation]:
    path = Path(path)
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    if not isinstance(raw, list):
        raise ValueError("Expected conversations.json to be a JSON array")

    conversations: list[ChatGptConversation] = []
    for item in raw:
        conv_id = item.get("conversation_id") or item.get("id", "")
        mapping = item.get("mapping", {})
        current_node = item.get("current_node")

        raw_messages = _walk_linear(mapping, current_node)

        messages: list[ChatGptMessage] = []
        for msg in raw_messages:
            role = (msg.get("author") or {}).get("role", "unknown")
            if role == "system":
                continue
            metadata = msg.get("metadata", {}) or {}
            messages.append(ChatGptMessage(
                role=role,
                content=_extract_text(msg),
                model_slug=metadata.get("model_slug"),
                create_time=_parse_timestamp(msg.get("create_time")),
                status=msg.get("status"),
            ))

        conversations.append(ChatGptConversation(
            conversation_id=conv_id,
            title=item.get("title", "Untitled"),
            create_time=_parse_timestamp(item.get("create_time")),
            update_time=_parse_timestamp(item.get("update_time")),
            default_model_slug=item.get("default_model_slug"),
            messages=messages,
            gizmo_id=item.get("gizmo_id"),
            is_archived=item.get("is_archived", False),
        ))

    return conversations


def find_conversation_by_id(
    conversations: list[ChatGptConversation],
    conversation_id: str,
) -> ChatGptConversation | None:
    for conv in conversations:
        if conv.conversation_id == conversation_id:
            return conv
        if conv.conversation_id and conversation_id.startswith(conv.conversation_id):
            return conv
    return None
