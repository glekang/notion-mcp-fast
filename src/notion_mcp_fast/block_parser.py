"""
Block parser for Notion's rich text format.

Notion stores rich text in a specific format that needs to be converted
to plain text for display.
"""

import json
from typing import Any


def parse_rich_text(rich_text: Any) -> str:
    """
    Parse Notion's rich text format to plain text.

    Rich text can be:
    - A string (already plain text)
    - A list of text segments: [["text", [["b"]]]] or [["text"]]
    - A dict with text/plain_text field
    - None

    Args:
        rich_text: Notion rich text in various formats

    Returns:
        Plain text string
    """
    if rich_text is None:
        return ""

    if isinstance(rich_text, str):
        return rich_text

    if isinstance(rich_text, dict):
        # Could be a single text object with plain_text
        if "plain_text" in rich_text:
            return rich_text["plain_text"]
        if "text" in rich_text:
            return rich_text["text"]
        return ""

    if isinstance(rich_text, list):
        parts = []
        for item in rich_text:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, list) and len(item) >= 1:
                # Format: [["text", [formatting]]] or [["text"]]
                parts.append(str(item[0]))
            elif isinstance(item, dict):
                # Format: {"text": {"content": "..."}, "plain_text": "..."}
                if "plain_text" in item:
                    parts.append(item["plain_text"])
                elif "text" in item and isinstance(item["text"], dict):
                    parts.append(item["text"].get("content", ""))
        return "".join(parts)

    return str(rich_text)


def get_title(properties: dict[str, Any] | None) -> str:
    """
    Extract title from Notion block properties.

    Args:
        properties: Block properties dict

    Returns:
        Title as plain text
    """
    if not properties:
        return ""

    # Try common title field names
    for key in ["title", "Name", "name", "Title"]:
        if key in properties:
            return parse_rich_text(properties[key])

    # Check for first property that looks like a title
    for value in properties.values():
        text = parse_rich_text(value)
        if text:
            return text

    return ""


def render_block(block_type: str, value: dict[str, Any] | None) -> str:
    """
    Render a Notion block to plain text with markdown-like formatting.

    Args:
        block_type: The type of block (text, header, bulleted_list, etc.)
        value: The block's value/content

    Returns:
        Rendered text with appropriate formatting
    """
    if value is None:
        return ""

    # Get the text content
    title = parse_rich_text(value.get("title", value.get("text", value.get("rich_text", ""))))

    # Apply formatting based on block type
    if block_type == "header":
        return f"# {title}"
    elif block_type == "sub_header":
        return f"## {title}"
    elif block_type == "sub_sub_header":
        return f"### {title}"
    elif block_type in ("bulleted_list", "bulleted_list_item"):
        return f"• {title}"
    elif block_type in ("numbered_list", "numbered_list_item"):
        return f"1. {title}"
    elif block_type == "to_do":
        checked = value.get("checked", False)
        checkbox = "[x]" if checked else "[ ]"
        return f"{checkbox} {title}"
    elif block_type == "toggle":
        return f"▸ {title}"
    elif block_type == "quote":
        return f"> {title}"
    elif block_type == "callout":
        icon = value.get("icon", {}).get("emoji", "💡")
        return f"{icon} {title}"
    elif block_type == "code":
        language = value.get("language", "")
        return f"```{language}\n{title}\n```"
    elif block_type == "equation":
        return f"$$ {title} $$"
    elif block_type == "divider":
        return "---"
    elif block_type == "bookmark":
        url = value.get("url", "")
        caption = title or url
        return f"[{caption}]({url})" if url else ""
    elif block_type == "image":
        url = value.get("source", [[""]])[0][0] if isinstance(value.get("source"), list) else ""
        caption = value.get("caption", "")
        return f"![{caption}]({url})" if url else f"[Image: {caption}]"
    elif block_type == "video":
        url = value.get("source", "")
        return f"[Video: {url}]" if url else "[Video]"
    elif block_type == "file":
        filename = value.get("title", "file")
        return f"[File: {filename}]"
    elif block_type == "pdf":
        return "[PDF Document]"
    elif block_type == "table":
        return "[Table]"
    elif block_type == "column_list":
        return ""  # Container, no direct content
    elif block_type == "column":
        return ""  # Container, no direct content
    elif block_type == "synced_block":
        return ""  # Reference to another block
    elif block_type == "template":
        return ""  # Template definition
    elif block_type == "child_page":
        return f"📄 {title}"
    elif block_type == "child_database":
        return f"🗃️ {title}"
    elif block_type == "link_to_page":
        return f"🔗 {title}"
    elif block_type == "embed":
        url = value.get("url", "")
        return f"[Embed: {url}]" if url else "[Embed]"
    elif block_type in ("text", "paragraph"):
        return title
    else:
        # Default: just return the text
        return title


def parse_block_content(block_data: dict[str, Any]) -> str:
    """
    Parse a full block record from the database.

    Args:
        block_data: Full block record from SQLite

    Returns:
        Rendered content as text
    """
    value = block_data.get("value", {})
    if not value:
        return ""

    block_type = value.get("type", "text")
    properties = value.get("properties", {})

    # For page blocks, get the title
    if block_type == "page":
        return get_title(properties)

    # For content blocks, render them
    return render_block(block_type, properties)


def blocks_to_text(blocks: list[dict[str, Any]], separator: str = "\n") -> str:
    """
    Convert a list of blocks to plain text.

    Args:
        blocks: List of block records
        separator: Text to join blocks with

    Returns:
        Combined text content
    """
    lines = []
    for block in blocks:
        text = parse_block_content(block)
        if text:
            lines.append(text)
    return separator.join(lines)


def safe_json_loads(data: Any) -> Any:
    """
    Safely parse JSON, returning empty dict on failure.

    Args:
        data: String or already-parsed data

    Returns:
        Parsed JSON or original data
    """
    if data is None:
        return {}
    if isinstance(data, (dict, list)):
        return data
    if isinstance(data, str):
        try:
            return json.loads(data)
        except (json.JSONDecodeError, ValueError):
            return {}
    if isinstance(data, bytes):
        try:
            return json.loads(data.decode("utf-8"))
        except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
            return {}
    return {}
