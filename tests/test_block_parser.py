"""Unit tests for block_parser.py"""

import sys
sys.path.insert(0, "/Users/wine_ny/side-project/notion-mcp-fast/src")

from notion_mcp_fast.block_parser import (
    parse_rich_text,
    get_title,
    render_block,
    safe_json_loads,
)


def test_bp01_string_rich_text():
    """BP-01: 문자열 리치 텍스트"""
    result = parse_rich_text("hello")
    assert result == "hello", f"Expected 'hello', got '{result}'"
    print("[PASS] BP-01 - 문자열 리치 텍스트")


def test_bp02_list_rich_text():
    """BP-02: 리스트 형식 리치 텍스트"""
    result = parse_rich_text([["text", [["b"]]]])
    assert result == "text", f"Expected 'text', got '{result}'"
    print("[PASS] BP-02 - 리스트 형식 리치 텍스트")


def test_bp03_dict_rich_text():
    """BP-03: dict 형식 리치 텍스트"""
    result = parse_rich_text({"plain_text": "hi"})
    assert result == "hi", f"Expected 'hi', got '{result}'"
    print("[PASS] BP-03 - dict 형식 리치 텍스트")


def test_bp04_none_input():
    """BP-04: None 입력"""
    result = parse_rich_text(None)
    assert result == "", f"Expected '', got '{result}'"
    print("[PASS] BP-04 - None 입력")


def test_bp05_empty_list():
    """BP-05: 빈 리스트"""
    result = parse_rich_text([])
    assert result == "", f"Expected '', got '{result}'"
    print("[PASS] BP-05 - 빈 리스트")


def test_bp06_header_block():
    """BP-06: header 블록 렌더링"""
    result = render_block("header", {"title": [["제목"]]})
    assert result == "# 제목", f"Expected '# 제목', got '{result}'"
    print("[PASS] BP-06 - header 블록 렌더링")


def test_bp07_bulleted_list():
    """BP-07: bulleted_list 렌더링"""
    result = render_block("bulleted_list", {"title": [["항목"]]})
    assert result == "• 항목", f"Expected '• 항목', got '{result}'"
    print("[PASS] BP-07 - bulleted_list 렌더링")


def test_bp08_todo_checked():
    """BP-08: to_do 체크됨"""
    result = render_block("to_do", {"title": [["할일"]], "checked": True})
    assert result == "[x] 할일", f"Expected '[x] 할일', got '{result}'"
    print("[PASS] BP-08 - to_do 체크됨")


def test_bp09_todo_unchecked():
    """BP-09: to_do 미체크"""
    result = render_block("to_do", {"title": [["할일"]], "checked": False})
    assert result == "[ ] 할일", f"Expected '[ ] 할일', got '{result}'"
    print("[PASS] BP-09 - to_do 미체크")


def test_bp10_code_block():
    """BP-10: code 블록"""
    result = render_block("code", {"title": [["print('hello')"]], "language": "python"})
    expected = "```python\nprint('hello')\n```"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("[PASS] BP-10 - code 블록")


def test_bp11_divider():
    """BP-11: divider 블록"""
    result = render_block("divider", {})
    assert result == "---", f"Expected '---', got '{result}'"
    print("[PASS] BP-11 - divider 블록")


def test_bp12_safe_json_loads_invalid():
    """BP-12: JSON 파싱 실패"""
    result = safe_json_loads("invalid json {")
    assert result == {}, f"Expected {{}}, got '{result}'"
    print("[PASS] BP-12 - JSON 파싱 실패")


def run_all_tests():
    """Run all block parser tests"""
    print("\n" + "="*50)
    print("Block Parser 단위 테스트")
    print("="*50 + "\n")

    tests = [
        test_bp01_string_rich_text,
        test_bp02_list_rich_text,
        test_bp03_dict_rich_text,
        test_bp04_none_input,
        test_bp05_empty_list,
        test_bp06_header_block,
        test_bp07_bulleted_list,
        test_bp08_todo_checked,
        test_bp09_todo_unchecked,
        test_bp10_code_block,
        test_bp11_divider,
        test_bp12_safe_json_loads_invalid,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {test.__doc__}: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {test.__doc__}: {e}")
            failed += 1

    print(f"\n결과: {passed}/{len(tests)} 통과")
    return passed, failed


if __name__ == "__main__":
    run_all_tests()
