from __future__ import annotations

import json
from pathlib import Path

import pytest

from parser2gis.chatgpt_export import (
    parse_conversations_json,
    find_conversation_by_id,
    conversation_to_markdown,
    conversation_to_handoff,
)


SAMPLE_CONVERSATIONS = [
    {
        "title": "Building a parser for 2GIS",
        "create_time": 1740000000,
        "update_time": 1740003600,
        "mapping": {
            "root": {
                "id": "root",
                "message": {
                    "id": "root",
                    "author": {"role": "system", "name": None, "metadata": {}},
                    "create_time": 1740000000,
                    "content": {"content_type": "text", "parts": []},
                    "status": "finished_successfully",
                    "end_turn": True,
                    "weight": 1.0,
                    "metadata": {},
                    "recipient": "all",
                },
                "parent": None,
                "children": ["msg1"],
            },
            "msg1": {
                "id": "msg1",
                "message": {
                    "id": "msg1",
                    "author": {"role": "user", "name": None, "metadata": {}},
                    "create_time": 1740000100,
                    "content": {"content_type": "text", "parts": ["How do I build a parser for 2GIS?"]},
                    "status": "finished_successfully",
                    "end_turn": True,
                    "weight": 1.0,
                    "metadata": {},
                    "recipient": "all",
                },
                "parent": "root",
                "children": ["msg2"],
            },
            "msg2": {
                "id": "msg2",
                "message": {
                    "id": "msg2",
                    "author": {"role": "assistant", "name": None, "metadata": {}},
                    "create_time": 1740000200,
                    "content": {"content_type": "text", "parts": ["You need to use the 2GIS API. Here's how:\n\n1. Find the city ID\n2. Search for organizations\n3. Parse the response"]},
                    "status": "finished_successfully",
                    "end_turn": True,
                    "weight": 1.0,
                    "metadata": {"model_slug": "gpt-4o"},
                    "recipient": "all",
                },
                "parent": "msg1",
                "children": ["msg3"],
            },
            "msg3": {
                "id": "msg3",
                "message": {
                    "id": "msg3",
                    "author": {"role": "user", "name": None, "metadata": {}},
                    "create_time": 1740000300,
                    "content": {"content_type": "text", "parts": ["Show me the code"]},
                    "status": "finished_successfully",
                    "end_turn": True,
                    "weight": 1.0,
                    "metadata": {},
                    "recipient": "all",
                },
                "parent": "msg2",
                "children": ["msg4"],
            },
            "msg4": {
                "id": "msg4",
                "message": {
                    "id": "msg4",
                    "author": {"role": "assistant", "name": None, "metadata": {}},
                    "create_time": 1740000400,
                    "content": {"content_type": "text", "parts": ["```python\nimport httpx\n\nclient = httpx.Client()\nresponse = client.get('https://api.2gis.ru/search')\n```"]},
                    "status": "finished_successfully",
                    "end_turn": True,
                    "weight": 1.0,
                    "metadata": {"model_slug": "gpt-4o"},
                    "recipient": "all",
                },
                "parent": "msg3",
                "children": [],
            },
        },
        "current_node": "msg4",
        "conversation_id": "6a4f46fe-b788-83eb-a1ea-7233173bc656",
        "default_model_slug": "gpt-4o",
        "is_archived": False,
    }
]


@pytest.fixture
def sample_export(tmp_path: Path) -> Path:
    path = tmp_path / "conversations.json"
    path.write_text(json.dumps(SAMPLE_CONVERSATIONS, ensure_ascii=False), encoding="utf-8")
    return path


def test_parse_conversations_json(sample_export: Path) -> None:
    conversations = parse_conversations_json(sample_export)
    assert len(conversations) == 1
    conv = conversations[0]
    assert conv.conversation_id == "6a4f46fe-b788-83eb-a1ea-7233173bc656"
    assert conv.title == "Building a parser for 2GIS"
    assert conv.default_model_slug == "gpt-4o"
    assert len(conv.messages) == 4


def test_find_conversation_by_id(sample_export: Path) -> None:
    conversations = parse_conversations_json(sample_export)
    conv = find_conversation_by_id(conversations, "6a4f46fe-b788-83eb-a1ea-7233173bc656")
    assert conv is not None
    assert conv.title == "Building a parser for 2GIS"

    conv2 = find_conversation_by_id(conversations, "nonexistent")
    assert conv2 is None


def test_conversation_to_markdown(sample_export: Path) -> None:
    conversations = parse_conversations_json(sample_export)
    conv = conversations[0]
    md = conversation_to_markdown(conv)
    assert "# Building a parser for 2GIS" in md
    assert "### User" in md
    assert "### Assistant" in md
    assert "How do I build a parser for 2GIS?" in md
    assert "```python" in md
    assert "gpt-4o" in md


def test_conversation_to_handoff(sample_export: Path) -> None:
    conversations = parse_conversations_json(sample_export)
    conv = conversations[0]
    handoff = conversation_to_handoff(conv)
    assert "# Handoff Document" in handoff
    assert "Context Summary" in handoff
    assert "Current State" in handoff
    assert "Next Steps" in handoff
    assert "# Building a parser for 2GIS" in handoff


def test_system_messages_skipped(sample_export: Path) -> None:
    conversations = parse_conversations_json(sample_export)
    conv = conversations[0]
    roles = [m.role for m in conv.messages]
    assert "system" not in roles
    assert roles == ["user", "assistant", "user", "assistant"]


def test_url_conversion_in_cli() -> None:
    from parser2gis.chatgpt_export.cli import main
    pass


def test_message_content_types(sample_export: Path) -> None:
    conversations = parse_conversations_json(sample_export)
    conv = conversations[0]
    assert conv.messages[0].content == "How do I build a parser for 2GIS?"
    assert conv.messages[2].content == "Show me the code"
    assert "import httpx" in conv.messages[3].content
    assert conv.messages[3].model_slug == "gpt-4o"
