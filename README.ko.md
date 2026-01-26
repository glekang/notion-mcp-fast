# notion-mcp-fast

[English](README.md)

macOS에서 Notion.app의 로컬 SQLite 캐시를 읽는 빠른 MCP 서버입니다.

## 왜 만들었나요?

공식 Notion API는 인증이 필요하고 rate limit이 있습니다. 이 MCP 서버는 Notion의 로컬 캐시에서 직접 읽어서:

- **API 호출 없음** - 네트워크 지연 없이 즉시 접근
- **Rate limit 없음** - 원하는 만큼 읽기 가능
- **거의 실시간 동기화** - Notion.app이 WebSocket으로 동기화, 1-3초 내 반영
- **오프라인 접근** - 인터넷 연결 없이도 작동
- **전체 컨텐츠 접근** - 메타데이터뿐 아니라 페이지 내용도 검색 가능

> ⚠️ **읽기 전용**: 이 서버는 Notion에 쓰기를 할 수 없습니다. 쓰기 작업은 [공식 Notion API](https://developers.notion.com/)를 사용하세요.

## 요구사항

- macOS (Notion.app의 로컬 SQLite 데이터베이스 사용)
- [Notion.app](https://www.notion.so/desktop) 설치 및 최소 1회 실행
- Python 3.10+

## 설치

```bash
# 클론 및 설치
git clone https://github.com/chat-prompt/notion-mcp-fast.git
cd notion-mcp-fast
uv sync

# 또는 직접 설치
uv pip install git+https://github.com/chat-prompt/notion-mcp-fast.git
```

## Claude Desktop에서 사용하기

Claude Desktop 설정 파일에 추가 (`~/Library/Application Support/Claude/claude_desktop_config.json`):

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

전역 설치한 경우:

```json
{
  "mcpServers": {
    "notion-local": {
      "command": "notion-mcp-fast"
    }
  }
}
```

## 사용 가능한 도구

| 도구 | 설명 |
|------|------|
| `list_pages` | 페이지 목록 (워크스페이스/상위 필터 가능) |
| `get_page` | 페이지 상세 정보 + 내용 |
| `search_pages` | 제목으로 페이지 검색 |
| `full_text_search` | 페이지 내용까지 전문 검색 |
| `list_databases` | 데이터베이스 목록 |
| `get_database` | 데이터베이스 스키마 조회 |
| `query_database` | 데이터베이스 레코드 조회 |
| `list_workspaces` | 워크스페이스 목록 |
| `get_summary` | 캐시 요약 정보 |

## 사용 예시

### 최근 페이지 목록
```
> list_pages(limit=10)
```

### 페이지 검색
```
> search_pages("회의록")
```

### 전문 검색
```
> full_text_search("프로젝트 마감")
```

### 페이지 내용 가져오기
```
> get_page("page-id-here", include_content=True)
```

### 데이터베이스 조회
```
> query_database("database-id-here", limit=20)
```

## 데이터 최신성

Notion.app의 로컬 캐시에서 데이터를 읽습니다:
- Notion.app이 동기화할 때 캐시 업데이트 (온라인 시 1-3초)
- 인메모리 캐시 TTL 5분
- 실시간 데이터가 필요하면 공식 Notion API 사용

## 문제 해결

### 데이터베이스를 찾을 수 없음

```
Notion database not found at ~/Library/Application Support/Notion/notion.db
```

**해결**: Notion.app을 최소 1회 실행하여 로컬 데이터베이스를 생성하세요.

### 페이지를 찾을 수 없음

원인:
1. Notion이 아직 동기화되지 않음 - Notion.app을 열고 잠시 대기
2. 다른 계정으로 로그인됨 - `meta_user_id` 감지 확인

### 권한 거부됨

macOS가 Application Support 접근을 차단할 수 있습니다. 시스템 환경설정 > 보안 및 개인 정보 보호 > 개인 정보 보호 > 전체 디스크 접근에서 터미널/IDE에 권한을 부여하세요.

## 배경: Notion에 왜 로컬 캐시가 있나요?

Notion 데스크톱 앱은 Electron 기반으로 만들어졌고, 오프라인 지원을 위해 로컬 SQLite 데이터베이스를 유지합니다. Notion에서 페이지를 열면 로컬에 캐시되어서:

- 인터넷 없이도 최근 본 페이지에 접근 가능
- 네트워크 끊김 중에도 작업 계속 가능
- 재방문 시 더 빠른 페이지 로딩

이 로컬 캐시(`notion.db`)에는 Notion이 내부적으로 사용하는 것과 동일한 블록 기반 데이터 구조가 들어있습니다 - 페이지, 데이터베이스, 텍스트 블록, 그리고 모든 속성들. 앱은 WebSocket으로 변경사항을 동기화하기 때문에 로컬 캐시는 놀라울 정도로 최신 상태를 유지합니다 (온라인 시 보통 서버보다 1-3초 뒤처지는 정도).

이 MCP 서버는 단순히 그 기존 캐시에서 읽기만 합니다 - 추가적인 동기화 메커니즘도, API 토큰도, rate limit도 없습니다.

## 작동 원리

Notion.app은 `~/Library/Application Support/Notion/notion.db`에 SQLite 캐시를 저장합니다. 이 MCP 서버는:

1. 읽기 전용 모드로 데이터베이스 열기
2. `meta_user_id`로 주 사용자 감지
3. 메타데이터(페이지, 데이터베이스) 5분간 캐시
4. 메모리 절약을 위해 블록 내용은 요청 시 로드
5. SQLite LIKE 쿼리로 전문 검색 수행

## 라이선스

MIT
