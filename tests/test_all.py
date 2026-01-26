#!/usr/bin/env python3
"""Run all tests for notion-mcp-fast"""

import sys
import os

# Add paths
sys.path.insert(0, "/Users/wine_ny/side-project/notion-mcp-fast/src")
sys.path.insert(0, "/Users/wine_ny/side-project/notion-mcp-fast")

from tests.test_block_parser import run_all_tests as run_parser_tests
from tests.test_integration import run_all_tests as run_integration_tests


def main():
    print("\n" + "🧪"*30)
    print("\n    NOTION-MCP-FAST 전체 테스트")
    print("\n" + "🧪"*30)

    # Block Parser 테스트
    parser_passed, parser_failed = run_parser_tests()

    # 통합 테스트
    int_passed, int_failed, int_skipped = run_integration_tests()

    # 최종 결과
    print("\n" + "="*60)
    print("📊 최종 테스트 결과")
    print("="*60)
    print(f"""
┌────────────────────┬────────┬────────┬────────┐
│      카테고리      │  통과  │  실패  │  스킵  │
├────────────────────┼────────┼────────┼────────┤
│ Block Parser       │   {parser_passed:2d}   │   {parser_failed:2d}   │   --   │
├────────────────────┼────────┼────────┼────────┤
│ 통합 테스트        │   {int_passed:2d}   │   {int_failed:2d}   │   {int_skipped:2d}   │
├────────────────────┼────────┼────────┼────────┤
│ 총계               │   {parser_passed + int_passed:2d}   │   {parser_failed + int_failed:2d}   │   {int_skipped:2d}   │
└────────────────────┴────────┴────────┴────────┘
""")

    total_failed = parser_failed + int_failed
    if total_failed == 0:
        print("✅ 모든 테스트 통과!")
    else:
        print(f"❌ {total_failed}개 테스트 실패")

    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
