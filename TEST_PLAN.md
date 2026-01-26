# notion-mcp-fast 테스트 계획

## 테스트 범위

### 1. 단위 테스트 (Unit Tests)

#### 1.1 block_parser.py

| ID | 테스트 케이스 | 입력 | 예상 출력 |
|----|--------------|------|----------|
| BP-01 | 문자열 리치 텍스트 | `"hello"` | `"hello"` |
| BP-02 | 리스트 형식 리치 텍스트 | `[["text", [["b"]]]]` | `"text"` |
| BP-03 | dict 형식 리치 텍스트 | `{"plain_text": "hi"}` | `"hi"` |
| BP-04 | None 입력 | `None` | `""` |
| BP-05 | 빈 리스트 | `[]` | `""` |
| BP-06 | header 블록 렌더링 | `{"title": [["제목"]]}` | `"# 제목"` |
| BP-07 | bulleted_list 렌더링 | `{"title": [["항목"]]}` | `"• 항목"` |
| BP-08 | to_do 체크됨 | `{"title": [["할일"]], "checked": True}` | `"[x] 할일"` |
| BP-09 | to_do 미체크 | `{"title": [["할일"]], "checked": False}` | `"[ ] 할일"` |
| BP-10 | code 블록 | `{"title": [["code"]], "language": "python"}` | ````python\ncode\n```` |
| BP-11 | divider 블록 | `{}` | `"---"` |
| BP-12 | JSON 파싱 실패 | `"invalid json {"` | `{}` |

#### 1.2 reader.py

| ID | 테스트 케이스 | 설명 |
|----|--------------|------|
| RD-01 | DB 존재 확인 | DB 파일 없을 때 FileNotFoundError |
| RD-02 | meta_user_id 감지 | 가장 많은 블록의 사용자 ID 반환 |
| RD-03 | 캐시 TTL | 5분 후 캐시 만료 확인 |
| RD-04 | 페이지 로드 | type='page' 블록만 로드 |
| RD-05 | 데이터베이스 로드 | collection_view_page 블록 로드 |
| RD-06 | 워크스페이스 로드 | space 테이블에서 로드 |
| RD-07 | 사용자 로드 | notion_user 테이블에서 로드 |
| RD-08 | 블록 내용 로드 | parent_id로 자식 블록 조회 |
| RD-09 | 재귀적 블록 로드 | max_depth 제한 동작 |
| RD-10 | 전체 텍스트 검색 | properties LIKE 쿼리 동작 |

---

### 2. 통합 테스트 (Integration Tests)

#### 2.1 MCP 도구 - 정상 케이스

| ID | 도구 | 테스트 케이스 | 검증 항목 |
|----|------|--------------|----------|
| IT-01 | `get_summary` | 기본 호출 | pages, databases, workspaces, users 카운트 |
| IT-02 | `list_workspaces` | 기본 호출 | id, name, pageCount 포함 |
| IT-03 | `list_pages` | limit 파라미터 | 결과 수 ≤ limit |
| IT-04 | `list_pages` | workspace 필터 | 해당 워크스페이스 페이지만 반환 |
| IT-05 | `list_pages` | parent_type 필터 | space/page/collection 필터 동작 |
| IT-06 | `get_page` | include_content=True | content 필드에 텍스트 포함 |
| IT-07 | `get_page` | include_content=False | content 필드 None |
| IT-08 | `search_pages` | 한글 검색 | 제목에 검색어 포함된 페이지 반환 |
| IT-09 | `search_pages` | 영문 검색 | 대소문자 무관 검색 |
| IT-10 | `full_text_search` | 내용 검색 | 제목이 아닌 내용에서 검색 |
| IT-11 | `list_databases` | 기본 호출 | id, name, collection_id 포함 |
| IT-12 | `list_databases` | workspace 필터 | 해당 워크스페이스 DB만 반환 |
| IT-13 | `get_database` | 스키마 조회 | properties에 타입 정보 포함 |
| IT-14 | `query_database` | 레코드 조회 | 스키마 속성명으로 매핑된 데이터 |
| IT-15 | `query_database` | limit 파라미터 | 결과 수 ≤ limit |

#### 2.2 MCP 도구 - 엣지 케이스

| ID | 도구 | 테스트 케이스 | 예상 결과 |
|----|------|--------------|----------|
| EC-01 | `get_page` | 존재하지 않는 ID | `None` 반환 |
| EC-02 | `get_database` | 존재하지 않는 ID | `None` 반환 |
| EC-03 | `query_database` | 존재하지 않는 ID | `{"records": [], "totalCount": 0}` |
| EC-04 | `search_pages` | 빈 검색어 | 모든 페이지 매칭 (limit까지) |
| EC-05 | `search_pages` | 특수문자만 | 빈 결과 또는 매칭된 결과 |
| EC-06 | `search_pages` | 매우 긴 검색어 | 정상 동작 (빈 결과 가능) |
| EC-07 | `list_pages` | 존재하지 않는 워크스페이스 | `{"pages": [], "totalCount": 0}` |
| EC-08 | `full_text_search` | SQL 인젝션 시도 | 안전하게 처리 |
| EC-09 | `query_database` | collection_id 없는 DB | 빈 결과 |
| EC-10 | `get_page` | 제목 없는 페이지 | title: "Untitled" |

#### 2.3 MCP 도구 - 에러 케이스

| ID | 테스트 케이스 | 예상 동작 |
|----|--------------|----------|
| ER-01 | DB 파일 없음 | FileNotFoundError 발생 |
| ER-02 | DB 파일 손상 | SQLite 에러 처리 |
| ER-03 | 권한 없음 | 적절한 에러 메시지 |

---

### 3. 성능 테스트 (Performance Tests)

| ID | 테스트 케이스 | 기준 |
|----|--------------|------|
| PF-01 | 캐시 로드 시간 | < 5초 (2만 페이지 기준) |
| PF-02 | 페이지 검색 시간 | < 100ms |
| PF-03 | 전체 텍스트 검색 시간 | < 2초 |
| PF-04 | 페이지 내용 로드 시간 | < 500ms |
| PF-05 | 메모리 사용량 | 메타데이터 캐시만 유지 확인 |

---

### 4. 데이터 무결성 테스트

| ID | 테스트 케이스 | 검증 항목 |
|----|--------------|----------|
| DI-01 | 페이지 ID 유일성 | 중복 ID 없음 |
| DI-02 | 부모-자식 관계 | parent_id가 유효한 블록 가리킴 |
| DI-03 | 워크스페이스 매핑 | 페이지의 parent_id가 space에 존재 |
| DI-04 | 데이터베이스 스키마 | collection_id로 스키마 조회 가능 |

---

## 테스트 실행 방법

### 수동 테스트
```bash
# 전체 테스트
uv run python tests/test_all.py

# 개별 모듈 테스트
uv run python -c "from tests.test_parser import run_tests; run_tests()"
```

### 자동화 테스트 (pytest)
```bash
uv run pytest tests/ -v
```

---

## 테스트 결과 기록 형식

```
[PASS/FAIL] {테스트ID} - {테스트명}
  입력: {입력값}
  예상: {예상값}
  실제: {실제값}
  시간: {소요시간}ms
```

---

## 체크리스트

### 테스트 전 확인사항
- [ ] Notion.app 설치 및 실행 이력 확인
- [ ] DB 파일 존재 확인 (`~/Library/Application Support/Notion/notion.db`)
- [ ] 충분한 테스트 데이터 존재 (페이지, 데이터베이스)

### 테스트 후 확인사항
- [ ] 모든 정상 케이스 통과
- [ ] 모든 엣지 케이스 적절히 처리
- [ ] 에러 케이스에서 예외 발생 없이 처리
- [ ] 성능 기준 충족
- [ ] 메모리 누수 없음
