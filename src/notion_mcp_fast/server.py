"""
MCP Server for Notion Local Cache.

Provides fast, read-only access to Notion data from local cache.
For write operations, use the official Notion API.
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from .reader import NotionLocalReader

mcp = FastMCP(
    "Notion Local Cache",
    instructions=(
        "Fast, read-only access to Notion data from the local Notion.app cache on macOS. "
        "Data freshness depends on Notion.app's last sync. "
        "For write operations, use the official Notion API."
    ),
)

_reader: NotionLocalReader | None = None


def get_reader() -> NotionLocalReader:
    """Get or create the NotionLocalReader instance."""
    global _reader
    if _reader is None:
        _reader = NotionLocalReader()
    return _reader


@mcp.tool()
def list_pages(
    workspace: str | None = None,
    parent_type: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """
    List pages from local cache.

    Args:
        workspace: Filter by workspace name (partial match)
        parent_type: Filter by parent type ('space', 'page', 'collection')
        limit: Maximum number of pages (default: 50)

    Returns:
        Dictionary with pages array and totalCount
    """
    reader = get_reader()

    # Find workspace ID if specified
    workspace_id = None
    if workspace:
        workspace_lower = workspace.lower()
        for ws in reader.workspaces.values():
            if workspace_lower in ws.get("name", "").lower():
                workspace_id = ws["id"]
                break
        if not workspace_id:
            return {"pages": [], "totalCount": 0}

    # Filter pages
    filtered = []
    for page in reader.pages.values():
        # Workspace filter (pages with parent_table='space')
        if workspace_id:
            if page.get("parent_table") != "space":
                continue
            if page.get("parent_id") != workspace_id:
                continue

        # Parent type filter
        if parent_type and page.get("parent_table") != parent_type:
            continue

        filtered.append(page)

    # Sort by last edited time (newest first)
    filtered.sort(
        key=lambda x: x.get("last_edited_time") or 0,
        reverse=True
    )

    total_count = len(filtered)
    page_list = filtered[:limit]

    results = []
    for page in page_list:
        results.append({
            "id": page.get("id"),
            "title": page.get("title") or "Untitled",
            "icon": page.get("icon"),
            "parent_type": page.get("parent_table"),
            "last_edited_time": page.get("last_edited_time"),
        })

    return {"pages": results, "totalCount": total_count}


@mcp.tool()
def get_page(page_id: str, include_content: bool = True) -> dict[str, Any] | None:
    """
    Get page details with optional content.

    Args:
        page_id: Page ID (UUID format)
        include_content: Whether to load page content blocks (default: True)

    Returns:
        Page details with content, or None if not found
    """
    reader = get_reader()

    if include_content:
        page = reader.get_page_content(page_id, max_depth=2)
    else:
        page = reader.pages.get(page_id)

    if not page:
        return None

    # Format content for display
    content_text = ""
    if include_content and "content" in page:
        lines = []
        for block in page.get("content", []):
            text = block.get("content", "")
            if text:
                lines.append(text)
            # Include first level children
            for child in block.get("children", []):
                child_text = child.get("content", "")
                if child_text:
                    lines.append(f"  {child_text}")
        content_text = "\n".join(lines)

    return {
        "id": page.get("id"),
        "title": page.get("title") or "Untitled",
        "icon": page.get("icon"),
        "cover": page.get("cover"),
        "parent_type": page.get("parent_table"),
        "parent_id": page.get("parent_id"),
        "created_time": page.get("created_time"),
        "last_edited_time": page.get("last_edited_time"),
        "content": content_text if include_content else None,
        "url": f"https://notion.so/{page.get('id', '').replace('-', '')}",
    }


@mcp.tool()
def search_pages(query: str, limit: int = 20) -> list[dict[str, Any]]:
    """
    Search pages by title.

    Args:
        query: Search query (case-insensitive)
        limit: Maximum results (default: 20)

    Returns:
        List of matching pages
    """
    reader = get_reader()
    pages = reader.search_pages(query, limit)

    results = []
    for page in pages:
        results.append({
            "id": page.get("id"),
            "title": page.get("title") or "Untitled",
            "icon": page.get("icon"),
            "parent_type": page.get("parent_table"),
            "last_edited_time": page.get("last_edited_time"),
            "url": f"https://notion.so/{page.get('id', '').replace('-', '')}",
        })

    return results


@mcp.tool()
def full_text_search(query: str, limit: int = 20) -> list[dict[str, Any]]:
    """
    Search page content (not just titles).

    This searches the actual content of pages, not just titles.
    May take 1-2 seconds on large databases.

    Args:
        query: Search query
        limit: Maximum results (default: 20)

    Returns:
        List of pages containing the query
    """
    reader = get_reader()
    pages = reader.full_text_search(query, limit)

    results = []
    for page in pages:
        results.append({
            "id": page.get("id"),
            "title": page.get("title") or "Untitled",
            "icon": page.get("icon"),
            "parent_type": page.get("parent_table"),
            "last_edited_time": page.get("last_edited_time"),
            "url": f"https://notion.so/{page.get('id', '').replace('-', '')}",
        })

    return results


@mcp.tool()
def list_databases(workspace: str | None = None) -> list[dict[str, Any]]:
    """
    List all databases.

    Args:
        workspace: Optional workspace name filter

    Returns:
        List of databases
    """
    reader = get_reader()

    # Find workspace ID if specified
    workspace_id = None
    if workspace:
        workspace_lower = workspace.lower()
        for ws in reader.workspaces.values():
            if workspace_lower in ws.get("name", "").lower():
                workspace_id = ws["id"]
                break
        if not workspace_id:
            return []

    results = []
    for db in reader.databases.values():
        # Workspace filter
        if workspace_id:
            if db.get("parent_table") != "space":
                continue
            if db.get("parent_id") != workspace_id:
                continue

        # Get schema for name
        schema = reader.get_database_schema(db["id"])
        name = "Untitled Database"
        if schema:
            name_value = schema.get("name")
            if isinstance(name_value, list) and name_value:
                name = name_value[0][0] if isinstance(name_value[0], list) else str(name_value[0])
            elif isinstance(name_value, str):
                name = name_value

        results.append({
            "id": db.get("id"),
            "name": name,
            "collection_id": db.get("collection_id"),
            "parent_type": db.get("parent_table"),
            "last_edited_time": db.get("last_edited_time"),
        })

    results.sort(key=lambda x: x.get("name", ""))
    return results


@mcp.tool()
def get_database(database_id: str) -> dict[str, Any] | None:
    """
    Get database details with schema.

    Args:
        database_id: Database ID

    Returns:
        Database details with schema, or None if not found
    """
    reader = get_reader()

    db = reader.databases.get(database_id)
    if not db:
        return None

    schema_info = reader.get_database_schema(database_id)
    if not schema_info:
        return None

    # Parse name
    name = "Untitled Database"
    name_value = schema_info.get("name")
    if isinstance(name_value, list) and name_value:
        name = name_value[0][0] if isinstance(name_value[0], list) else str(name_value[0])
    elif isinstance(name_value, str):
        name = name_value

    # Format schema for display
    properties = {}
    for prop_id, prop_info in schema_info.get("schema", {}).items():
        properties[prop_info.get("name", prop_id)] = {
            "id": prop_id,
            "type": prop_info.get("type", "text"),
        }

    return {
        "id": database_id,
        "name": name,
        "description": schema_info.get("description"),
        "icon": schema_info.get("icon"),
        "collection_id": db.get("collection_id"),
        "properties": properties,
        "last_edited_time": db.get("last_edited_time"),
        "url": f"https://notion.so/{database_id.replace('-', '')}",
    }


@mcp.tool()
def query_database(database_id: str, limit: int = 50) -> dict[str, Any]:
    """
    Get records from a database.

    Args:
        database_id: Database ID
        limit: Maximum records (default: 50)

    Returns:
        Dictionary with records and schema info
    """
    reader = get_reader()

    db = reader.databases.get(database_id)
    if not db:
        return {"records": [], "totalCount": 0}

    records = reader.get_database_records(database_id, limit)
    schema_info = reader.get_database_schema(database_id)

    # Get property names from schema
    property_names = []
    if schema_info:
        for prop_info in schema_info.get("schema", {}).values():
            property_names.append(prop_info.get("name", ""))

    return {
        "records": records,
        "totalCount": len(records),
        "properties": property_names,
    }


@mcp.tool()
def list_workspaces() -> list[dict[str, Any]]:
    """
    List all workspaces.

    Returns:
        List of workspaces
    """
    reader = get_reader()

    results = []
    for ws in reader.workspaces.values():
        # Count pages in this workspace
        page_count = sum(
            1 for p in reader.pages.values()
            if p.get("parent_table") == "space" and p.get("parent_id") == ws["id"]
        )

        results.append({
            "id": ws.get("id"),
            "name": ws.get("name") or "Unnamed Workspace",
            "icon": ws.get("icon"),
            "domain": ws.get("domain"),
            "pageCount": page_count,
        })

    results.sort(key=lambda x: x.get("name", ""))
    return results


@mcp.tool()
def get_summary() -> dict[str, Any]:
    """
    Get a summary of the local Notion cache.

    Returns:
        Summary with counts of pages, databases, workspaces
    """
    reader = get_reader()
    return reader.get_summary()


def main():
    """Run the MCP server."""
    mcp.run()
