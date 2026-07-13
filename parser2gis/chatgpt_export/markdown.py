from __future__ import annotations

from datetime import datetime

from parser2gis.chatgpt_export.parser import ChatGptConversation, ChatGptMessage


def _format_time(dt: datetime | None) -> str:
    if dt is None:
        return "unknown"
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def _role_label(role: str) -> str:
    return {"user": "User", "assistant": "Assistant", "tool": "Tool"}.get(role, role.capitalize())


def conversation_to_markdown(conv: ChatGptConversation, include_metadata: bool = True) -> str:
    lines: list[str] = []

    lines.append(f"# {conv.title}")
    lines.append("")

    if include_metadata:
        parts = []
        if conv.create_time:
            parts.append(f"**Created:** {_format_time(conv.create_time)}")
        if conv.update_time:
            parts.append(f"**Updated:** {_format_time(conv.update_time)}")
        if conv.default_model_slug:
            parts.append(f"**Model:** {conv.default_model_slug}")
        parts.append(f"**Messages:** {len(conv.messages)}")
        if conv.gizmo_id:
            parts.append(f"**GPT:** {conv.gizmo_id}")
        lines.append(" | ".join(parts))
        lines.append("")
        lines.append("---")
        lines.append("")

    for i, msg in enumerate(conv.messages):
        label = _role_label(msg.role)
        timestamp = f" ({_format_time(msg.create_time)})" if msg.create_time else ""
        model = f" [{msg.model_slug}]" if msg.model_slug else ""

        lines.append(f"### {label}{timestamp}{model}")
        lines.append("")

        content = msg.content.strip()
        if not content:
            content = "*[empty message]*"

        if msg.role == "assistant" and "```" in content:
            lines.append(content)
        elif msg.role == "tool":
            lines.append(f"```\n{content}\n```")
        else:
            lines.append(content)

        lines.append("")
        lines.append("---" if i < len(conv.messages) - 1 else "")
        lines.append("")

    return "\n".join(lines)


def conversation_to_handoff(conv: ChatGptConversation) -> str:
    lines: list[str] = []

    lines.append("# Handoff Document")
    lines.append("")
    lines.append(f"**Conversation:** {conv.title}")
    lines.append(f"**ID:** {conv.conversation_id}")
    lines.append(f"**Date:** {_format_time(conv.create_time)}")
    if conv.default_model_slug:
        lines.append(f"**Model:** {conv.default_model_slug}")
    lines.append(f"**Total messages:** {len(conv.messages)}")
    lines.append("")

    lines.append("---")
    lines.append("")

    lines.append("## Context Summary")
    lines.append("")
    lines.append("*This section should be filled in manually after reviewing the conversation.*")
    lines.append("")

    lines.append("## Current State")
    lines.append("")
    lines.append("*Describe what was accomplished and what remains.*")
    lines.append("")

    lines.append("## Key Decisions")
    lines.append("")
    lines.append("*List important decisions made during this conversation.*")
    lines.append("")

    lines.append("## Next Steps")
    lines.append("")
    lines.append("*Outline what should happen next.*")
    lines.append("")

    lines.append("---")
    lines.append("")

    lines.append("## Full Conversation Log")
    lines.append("")
    lines.append(conversation_to_markdown(conv))

    return "\n".join(lines)
