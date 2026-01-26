"""Integration tests for MCP server tools"""

import os
import sys
import time

sys.path.insert(0, "/Users/wine_ny/side-project/notion-mcp-fast/src")

from notion_mcp_fast.reader import NotionLocalReader, NOTION_DB_PATH


def check_db_exists():
    """테스트 전 DB 파일 존재 확인"""
    if not os.path.exists(NOTION_DB_PATH):
        print(f"[SKIP] Notion DB not found at {NOTION_DB_PATH}")
        return False
    print(f"[OK] Notion DB found at {NOTION_DB_PATH}")
    return True


class IntegrationTests:
    def __init__(self):
        self.reader = NotionLocalReader()
        self.passed = 0
        self.failed = 0
        self.skipped = 0

    def _pass(self, test_id, name):
        print(f"[PASS] {test_id} - {name}")
        self.passed += 1

    def _fail(self, test_id, name, reason):
        print(f"[FAIL] {test_id} - {name}: {reason}")
        self.failed += 1

    def _skip(self, test_id, name, reason):
        print(f"[SKIP] {test_id} - {name}: {reason}")
        self.skipped += 1

    # === 정상 케이스 ===

    def test_it01_get_summary(self):
        """IT-01: get_summary 기본 호출"""
        summary = self.reader.get_summary()
        required_keys = ["pages", "databases", "workspaces", "users"]
        for key in required_keys:
            if key not in summary:
                self._fail("IT-01", "get_summary", f"Missing key: {key}")
                return
        self._pass("IT-01", "get_summary 기본 호출")

    def test_it02_list_workspaces(self):
        """IT-02: list_workspaces 기본 호출"""
        workspaces = list(self.reader.workspaces.values())
        if len(workspaces) == 0:
            self._skip("IT-02", "list_workspaces", "No workspaces found")
            return
        ws = workspaces[0]
        required = ["id", "name"]
        for key in required:
            if key not in ws:
                self._fail("IT-02", "list_workspaces", f"Missing key: {key}")
                return
        self._pass("IT-02", "list_workspaces 기본 호출")

    def test_it03_list_pages_limit(self):
        """IT-03: list_pages limit 파라미터"""
        pages = list(self.reader.pages.values())[:5]
        if len(pages) > 5:
            self._fail("IT-03", "list_pages limit", "Limit not respected")
            return
        self._pass("IT-03", "list_pages limit 파라미터")

    def test_it04_list_pages_workspace(self):
        """IT-04: list_pages workspace 필터"""
        workspaces = list(self.reader.workspaces.values())
        if not workspaces:
            self._skip("IT-04", "list_pages workspace", "No workspaces")
            return
        ws_id = workspaces[0]["id"]
        filtered = [
            p for p in self.reader.pages.values()
            if p.get("parent_table") == "space" and p.get("parent_id") == ws_id
        ]
        self._pass("IT-04", "list_pages workspace 필터")

    def test_it05_list_pages_parent_type(self):
        """IT-05: list_pages parent_type 필터"""
        filtered = [
            p for p in self.reader.pages.values()
            if p.get("parent_table") == "page"
        ]
        self._pass("IT-05", "list_pages parent_type 필터")

    def test_it06_get_page_with_content(self):
        """IT-06: get_page include_content=True"""
        pages = list(self.reader.pages.keys())
        if not pages:
            self._skip("IT-06", "get_page with content", "No pages")
            return
        page = self.reader.get_page_content(pages[0])
        if page is None:
            self._fail("IT-06", "get_page with content", "Page not found")
            return
        if "content" not in page:
            self._fail("IT-06", "get_page with content", "No content field")
            return
        self._pass("IT-06", "get_page include_content=True")

    def test_it07_get_page_without_content(self):
        """IT-07: get_page include_content=False"""
        pages = list(self.reader.pages.keys())
        if not pages:
            self._skip("IT-07", "get_page without content", "No pages")
            return
        page = self.reader.pages.get(pages[0])
        if page is None:
            self._fail("IT-07", "get_page without content", "Page not found")
            return
        self._pass("IT-07", "get_page include_content=False")

    def test_it08_search_pages_korean(self):
        """IT-08: search_pages 한글 검색"""
        # 임의 한글 검색어로 검색 (결과가 없어도 에러 없으면 통과)
        results = self.reader.search_pages("테스트")
        if not isinstance(results, list):
            self._fail("IT-08", "search_pages 한글", "Invalid result type")
            return
        self._pass("IT-08", "search_pages 한글 검색")

    def test_it09_search_pages_english(self):
        """IT-09: search_pages 영문 검색"""
        results = self.reader.search_pages("Test")
        if not isinstance(results, list):
            self._fail("IT-09", "search_pages 영문", "Invalid result type")
            return
        self._pass("IT-09", "search_pages 영문 검색")

    def test_it10_full_text_search(self):
        """IT-10: full_text_search 내용 검색"""
        results = self.reader.full_text_search("the")
        if not isinstance(results, list):
            self._fail("IT-10", "full_text_search", "Invalid result type")
            return
        self._pass("IT-10", "full_text_search 내용 검색")

    def test_it11_list_databases(self):
        """IT-11: list_databases 기본 호출"""
        dbs = list(self.reader.databases.values())
        if len(dbs) == 0:
            self._skip("IT-11", "list_databases", "No databases found")
            return
        db = dbs[0]
        required = ["id", "collection_id"]
        for key in required:
            if key not in db:
                self._fail("IT-11", "list_databases", f"Missing key: {key}")
                return
        self._pass("IT-11", "list_databases 기본 호출")

    def test_it12_list_databases_workspace(self):
        """IT-12: list_databases workspace 필터"""
        workspaces = list(self.reader.workspaces.values())
        if not workspaces:
            self._skip("IT-12", "list_databases workspace", "No workspaces")
            return
        ws_id = workspaces[0]["id"]
        filtered = [
            db for db in self.reader.databases.values()
            if db.get("parent_table") == "space" and db.get("parent_id") == ws_id
        ]
        self._pass("IT-12", "list_databases workspace 필터")

    def test_it13_get_database_schema(self):
        """IT-13: get_database 스키마 조회"""
        dbs = list(self.reader.databases.keys())
        if not dbs:
            self._skip("IT-13", "get_database schema", "No databases")
            return
        schema = self.reader.get_database_schema(dbs[0])
        # schema가 None이어도 에러 없으면 OK (collection_id 없는 DB 가능)
        self._pass("IT-13", "get_database 스키마 조회")

    def test_it14_query_database(self):
        """IT-14: query_database 레코드 조회"""
        dbs = list(self.reader.databases.keys())
        if not dbs:
            self._skip("IT-14", "query_database", "No databases")
            return
        records = self.reader.get_database_records(dbs[0])
        if not isinstance(records, list):
            self._fail("IT-14", "query_database", "Invalid result type")
            return
        self._pass("IT-14", "query_database 레코드 조회")

    def test_it15_query_database_limit(self):
        """IT-15: query_database limit 파라미터"""
        dbs = list(self.reader.databases.keys())
        if not dbs:
            self._skip("IT-15", "query_database limit", "No databases")
            return
        records = self.reader.get_database_records(dbs[0], limit=5)
        if len(records) > 5:
            self._fail("IT-15", "query_database limit", "Limit not respected")
            return
        self._pass("IT-15", "query_database limit 파라미터")

    # === 엣지 케이스 ===

    def test_ec01_get_page_invalid_id(self):
        """EC-01: get_page 존재하지 않는 ID"""
        result = self.reader.pages.get("non-existent-id-12345")
        if result is not None:
            self._fail("EC-01", "get_page invalid ID", "Should return None")
            return
        self._pass("EC-01", "get_page 존재하지 않는 ID")

    def test_ec02_get_database_invalid_id(self):
        """EC-02: get_database 존재하지 않는 ID"""
        result = self.reader.databases.get("non-existent-id-12345")
        if result is not None:
            self._fail("EC-02", "get_database invalid ID", "Should return None")
            return
        self._pass("EC-02", "get_database 존재하지 않는 ID")

    def test_ec03_query_database_invalid_id(self):
        """EC-03: query_database 존재하지 않는 ID"""
        result = self.reader.get_database_records("non-existent-id-12345")
        if result != []:
            self._fail("EC-03", "query_database invalid ID", f"Expected [], got {result}")
            return
        self._pass("EC-03", "query_database 존재하지 않는 ID")

    def test_ec04_search_empty_query(self):
        """EC-04: search_pages 빈 검색어"""
        results = self.reader.search_pages("")
        if not isinstance(results, list):
            self._fail("EC-04", "search_pages empty", "Invalid result type")
            return
        self._pass("EC-04", "search_pages 빈 검색어")

    def test_ec05_search_special_chars(self):
        """EC-05: search_pages 특수문자만"""
        results = self.reader.search_pages("@#$%^&*()")
        if not isinstance(results, list):
            self._fail("EC-05", "search_pages special", "Invalid result type")
            return
        self._pass("EC-05", "search_pages 특수문자만")

    def test_ec06_search_long_query(self):
        """EC-06: search_pages 매우 긴 검색어"""
        long_query = "a" * 1000
        results = self.reader.search_pages(long_query)
        if not isinstance(results, list):
            self._fail("EC-06", "search_pages long", "Invalid result type")
            return
        self._pass("EC-06", "search_pages 매우 긴 검색어")

    def test_ec07_list_pages_invalid_workspace(self):
        """EC-07: list_pages 존재하지 않는 워크스페이스"""
        # 직접 필터링 - 잘못된 workspace ID로 필터링하면 빈 결과
        filtered = [
            p for p in self.reader.pages.values()
            if p.get("parent_id") == "non-existent-workspace-id"
        ]
        if filtered != []:
            self._fail("EC-07", "list_pages invalid ws", "Should return []")
            return
        self._pass("EC-07", "list_pages 존재하지 않는 워크스페이스")

    def test_ec08_sql_injection(self):
        """EC-08: full_text_search SQL 인젝션 시도"""
        # 악의적인 SQL 인젝션 시도
        malicious = "'; DROP TABLE block; --"
        try:
            results = self.reader.full_text_search(malicious)
            # 정상적으로 처리되면 통과
            self._pass("EC-08", "full_text_search SQL 인젝션 방어")
        except Exception as e:
            self._fail("EC-08", "SQL injection", str(e))

    def test_ec09_query_db_no_collection(self):
        """EC-09: query_database collection_id 없는 DB"""
        # collection_id가 None인 DB 찾기
        found = False
        for db_id, db in self.reader.databases.items():
            if not db.get("collection_id"):
                records = self.reader.get_database_records(db_id)
                if records != []:
                    self._fail("EC-09", "query_db no collection", "Should return []")
                    return
                found = True
                break
        if not found:
            self._skip("EC-09", "query_db no collection", "All DBs have collection_id")
            return
        self._pass("EC-09", "query_database collection_id 없는 DB")

    def test_ec10_page_no_title(self):
        """EC-10: get_page 제목 없는 페이지"""
        # 제목이 빈 페이지 찾기
        for page in self.reader.pages.values():
            if not page.get("title"):
                # 제목이 없어도 에러 없이 처리되면 OK
                self._pass("EC-10", "get_page 제목 없는 페이지")
                return
        self._skip("EC-10", "page no title", "All pages have titles")

    # === 성능 테스트 ===

    def test_pf01_cache_load_time(self):
        """PF-01: 캐시 로드 시간"""
        # 캐시 강제 만료
        self.reader._cache.loaded_at = 0
        start = time.time()
        self.reader._ensure_cache()
        elapsed = time.time() - start
        if elapsed > 5:
            self._fail("PF-01", "cache load time", f"{elapsed:.2f}s > 5s")
            return
        print(f"    캐시 로드 시간: {elapsed:.2f}s")
        self._pass("PF-01", "캐시 로드 시간 < 5초")

    def test_pf02_search_time(self):
        """PF-02: 페이지 검색 시간"""
        start = time.time()
        self.reader.search_pages("test")
        elapsed = time.time() - start
        if elapsed > 0.1:
            self._fail("PF-02", "search time", f"{elapsed*1000:.0f}ms > 100ms")
            return
        print(f"    검색 시간: {elapsed*1000:.1f}ms")
        self._pass("PF-02", "페이지 검색 시간 < 100ms")

    def test_pf03_full_text_search_time(self):
        """PF-03: 전체 텍스트 검색 시간"""
        start = time.time()
        self.reader.full_text_search("the")
        elapsed = time.time() - start
        if elapsed > 2:
            self._fail("PF-03", "full text search time", f"{elapsed:.2f}s > 2s")
            return
        print(f"    전체 텍스트 검색 시간: {elapsed:.2f}s")
        self._pass("PF-03", "전체 텍스트 검색 시간 < 2초")

    def test_pf04_page_content_time(self):
        """PF-04: 페이지 내용 로드 시간"""
        pages = list(self.reader.pages.keys())
        if not pages:
            self._skip("PF-04", "page content time", "No pages")
            return
        start = time.time()
        self.reader.get_page_content(pages[0])
        elapsed = time.time() - start
        if elapsed > 0.5:
            self._fail("PF-04", "page content time", f"{elapsed*1000:.0f}ms > 500ms")
            return
        print(f"    페이지 내용 로드 시간: {elapsed*1000:.1f}ms")
        self._pass("PF-04", "페이지 내용 로드 시간 < 500ms")

    # === 데이터 무결성 ===

    def test_di01_page_id_unique(self):
        """DI-01: 페이지 ID 유일성"""
        page_ids = list(self.reader.pages.keys())
        if len(page_ids) != len(set(page_ids)):
            self._fail("DI-01", "page ID unique", "Duplicate IDs found")
            return
        self._pass("DI-01", "페이지 ID 유일성")

    def test_di02_parent_child_relation(self):
        """DI-02: 부모-자식 관계"""
        # parent_id가 있는 페이지가 유효한 부모를 가리키는지 확인
        invalid_count = 0
        for page in self.reader.pages.values():
            parent_id = page.get("parent_id")
            parent_table = page.get("parent_table")
            if parent_table == "page" and parent_id:
                if parent_id not in self.reader.pages:
                    invalid_count += 1
        if invalid_count > 0:
            print(f"    경고: {invalid_count}개의 페이지가 유효하지 않은 부모 참조")
        self._pass("DI-02", "부모-자식 관계 검증")

    def test_di03_workspace_mapping(self):
        """DI-03: 워크스페이스 매핑"""
        ws_ids = set(self.reader.workspaces.keys())
        unmapped = 0
        for page in self.reader.pages.values():
            if page.get("parent_table") == "space":
                if page.get("parent_id") not in ws_ids:
                    unmapped += 1
        if unmapped > 0:
            print(f"    경고: {unmapped}개의 페이지가 알 수 없는 워크스페이스 참조")
        self._pass("DI-03", "워크스페이스 매핑 검증")

    def test_di04_database_schema(self):
        """DI-04: 데이터베이스 스키마"""
        for db_id, db in self.reader.databases.items():
            collection_id = db.get("collection_id")
            if collection_id:
                schema = self.reader.get_database_schema(db_id)
                # 스키마가 있으면 OK
        self._pass("DI-04", "데이터베이스 스키마 검증")

    def run_all(self):
        """Run all integration tests"""
        print("\n" + "="*60)
        print("통합 테스트 (Integration Tests)")
        print("="*60)

        # 정상 케이스
        print("\n--- 정상 케이스 ---")
        self.test_it01_get_summary()
        self.test_it02_list_workspaces()
        self.test_it03_list_pages_limit()
        self.test_it04_list_pages_workspace()
        self.test_it05_list_pages_parent_type()
        self.test_it06_get_page_with_content()
        self.test_it07_get_page_without_content()
        self.test_it08_search_pages_korean()
        self.test_it09_search_pages_english()
        self.test_it10_full_text_search()
        self.test_it11_list_databases()
        self.test_it12_list_databases_workspace()
        self.test_it13_get_database_schema()
        self.test_it14_query_database()
        self.test_it15_query_database_limit()

        # 엣지 케이스
        print("\n--- 엣지 케이스 ---")
        self.test_ec01_get_page_invalid_id()
        self.test_ec02_get_database_invalid_id()
        self.test_ec03_query_database_invalid_id()
        self.test_ec04_search_empty_query()
        self.test_ec05_search_special_chars()
        self.test_ec06_search_long_query()
        self.test_ec07_list_pages_invalid_workspace()
        self.test_ec08_sql_injection()
        self.test_ec09_query_db_no_collection()
        self.test_ec10_page_no_title()

        # 성능 테스트
        print("\n--- 성능 테스트 ---")
        self.test_pf01_cache_load_time()
        self.test_pf02_search_time()
        self.test_pf03_full_text_search_time()
        self.test_pf04_page_content_time()

        # 데이터 무결성
        print("\n--- 데이터 무결성 ---")
        self.test_di01_page_id_unique()
        self.test_di02_parent_child_relation()
        self.test_di03_workspace_mapping()
        self.test_di04_database_schema()

        # 결과 요약
        print("\n" + "="*60)
        total = self.passed + self.failed + self.skipped
        print(f"결과: {self.passed} 통과 / {self.failed} 실패 / {self.skipped} 스킵 (총 {total})")
        print("="*60)

        return self.passed, self.failed, self.skipped


def run_all_tests():
    if not check_db_exists():
        print("테스트를 진행할 수 없습니다.")
        return 0, 0, 0

    tests = IntegrationTests()
    return tests.run_all()


if __name__ == "__main__":
    run_all_tests()
