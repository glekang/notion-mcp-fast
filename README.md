# notion-mcp-fast

[한국어](README.ko.md)

Fast MCP server for Notion - reads from Notion.app's local SQLite cache on macOS.

## Why?

The official Notion API requires authentication and has rate limits. This MCP server reads directly from Notion's local cache, providing:

- **No API calls** - instant access without network latency
- **No rate limits** - read as much as you want
- **Near real-time sync** - Notion.app syncs via WebSocket, updates reflect in 1-3 seconds
- **Offline access** - works without internet connection
- **Full content access** - search page content, not just metadata

> ⚠️ **Read-only**: This server cannot write to Notion. For write operations, use the [official Notion API](https://developers.notion.com/).

## Requirements

- macOS (uses Notion.app's local SQLite database)
- [Notion.app](https://www.notion.so/desktop) installed and opened at least once
- Python 3.10+

## Installation

```bash
# Clone and install
git clone https://github.com/chat-prompt/notion-mcp-fast.git
cd notion-mcp-fast
uv sync

# Or install directly
uv pip install git+https://github.com/chat-prompt/notion-mcp-fast.git
```

## Usage with Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "notion-local": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/notion-mcp-fast", "notion-mcp-fast"]
    }
  }
}
```

Or if installed globally:

```json
{
  "mcpServers": {
    "notion-local": {
      "command": "notion-mcp-fast"
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `list_pages` | List pages with optional workspace/parent filters |
| `get_page` | Get page details with content |
| `search_pages` | Search pages by title |
| `full_text_search` | Search page content (not just titles) |
| `list_databases` | List all databases |
| `get_database` | Get database schema |
| `query_database` | Get records from a database |
| `list_workspaces` | List all workspaces |
| `get_summary` | Get cache summary |

## Examples

### List Recent Pages
```
> list_pages(limit=10)
```

### Search Pages
```
> search_pages("meeting notes")
```

### Full Text Search
```
> full_text_search("project deadline")
```

### Get Page Content
```
> get_page("page-id-here", include_content=True)
```

### Query Database
```
> query_database("database-id-here", limit=20)
```

## Data Freshness

Data is read from Notion.app's local cache:
- Cache updates when Notion.app syncs
- In-memory cache has 5-minute TTL
- For real-time data, use the official Notion API

## Troubleshooting

### Database Not Found

```
Notion database not found at ~/Library/Application Support/Notion/notion.db
```

**Solution**: Open Notion.app at least once to create the local database.

### No Pages Found

This usually means:
1. Notion hasn't synced yet - open Notion.app and wait
2. You're logged into a different account - check `meta_user_id` detection

### Permission Denied

macOS may block access to Application Support. Grant Terminal/IDE full disk access in System Preferences > Security & Privacy > Privacy > Full Disk Access.

## Background: Why Does Notion Have a Local Cache?

Notion's desktop app is built on Electron and maintains a local SQLite database for offline support. When you open any page in Notion, it gets cached locally so you can:

- Access recently viewed pages without internet
- Continue working during network interruptions
- Experience faster page loads on subsequent visits

This local cache (`notion.db`) contains the same block-based data structure that Notion uses internally - pages, databases, text blocks, and all their properties. The app syncs changes via WebSocket, so the local cache stays remarkably fresh (typically 1-3 seconds behind the server when online).

This MCP server simply reads from that existing cache - no additional sync mechanism, no API tokens, no rate limits.

## How It Works

Notion.app stores a SQLite cache at `~/Library/Application Support/Notion/notion.db`. This MCP server:

1. Opens the database in read-only mode
2. Detects the primary user via `meta_user_id`
3. Caches metadata (pages, databases) for 5 minutes
4. Loads content blocks on-demand to conserve memory
5. Uses SQLite LIKE queries for full-text search

## License

MIT
