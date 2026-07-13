from __future__ import annotations

import argparse
import sys
from pathlib import Path

from parser2gis.chatgpt_export import (
    parse_conversations_json,
    find_conversation_by_id,
    conversation_to_markdown,
    conversation_to_handoff,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="chatgpt-export",
        description="Export a ChatGPT conversation from conversations.json to markdown",
    )
    parser.add_argument("export_path", type=Path, help="Path to conversations.json from ChatGPT data export")
    parser.add_argument("conversation_id", help="Conversation ID or URL (e.g. 6a4f46fe-b788-83eb-a1ea-7233173bc656)")
    parser.add_argument("--output", "-o", type=Path, default=None, help="Output .md file path")
    parser.add_argument("--handoff", action="store_true", help="Generate a handoff document instead of plain markdown")

    args = parser.parse_args()

    conv_id = args.conversation_id
    if conv_id.startswith("https://chatgpt.com/c/"):
        conv_id = conv_id.replace("https://chatgpt.com/c/", "").split("?")[0]

    if not args.export_path.exists():
        print(f"File not found: {args.export_path}", file=sys.stderr)
        sys.exit(1)

    conversations = parse_conversations_json(args.export_path)
    conv = find_conversation_by_id(conversations, conv_id)
    if not conv:
        print(f"Conversation {conv_id} not found in {args.export_path}", file=sys.stderr)
        print(f"Available conversations: {len(conversations)} total", file=sys.stderr)
        sys.exit(1)

    if args.handoff:
        md = conversation_to_handoff(conv)
    else:
        md = conversation_to_markdown(conv)

    output_path = args.output or Path(f"chatgpt-{conv_id[:8]}.md")
    output_path.write_text(md, encoding="utf-8")
    print(f"Exported {len(conv.messages)} messages to {output_path}")


if __name__ == "__main__":
    main()
