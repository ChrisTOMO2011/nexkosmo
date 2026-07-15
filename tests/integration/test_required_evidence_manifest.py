from pathlib import Path


def test_no_blocking_test_is_marked_skipped():
    root = Path("tests")
    current_file = Path(__file__).resolve()

    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in root.rglob("test_*.py")
        if path.resolve() != current_file
    )

    forbidden = (
        "pytest." + "skip(",
        "@pytest.mark." + "skip",
        "@pytest.mark." + "xfail",
    )

    assert not any(marker in source for marker in forbidden)
