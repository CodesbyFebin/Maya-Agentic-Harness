import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from harness.tools import filesystem
from harness import backend_real


@pytest.fixture
def allowed_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "docs"
    root.mkdir()
    monkeypatch.setenv("MAYA_ALLOWED_ROOTS", str(root))
    return root


def test_reads_file_under_allowed_root(allowed_root: Path) -> None:
    target = allowed_root / "note.txt"
    target.write_text("hello", encoding="utf-8")
    assert filesystem.read_file(str(target)) == "hello"


def test_path_traversal_is_blocked(allowed_root: Path) -> None:
    outside = allowed_root.parent / "secret.txt"
    outside.write_text("secret", encoding="utf-8")
    with pytest.raises(PermissionError):
        filesystem.read_file(str(allowed_root / ".." / "secret.txt"))


def test_sibling_prefix_escape_is_blocked(allowed_root: Path) -> None:
    sibling = allowed_root.parent / "docs_evil"
    sibling.mkdir()
    target = sibling / "secret.txt"
    target.write_text("secret", encoding="utf-8")
    with pytest.raises(PermissionError):
        filesystem.read_file(str(target))


def test_symlink_escape_is_blocked(allowed_root: Path) -> None:
    outside = allowed_root.parent / "outside.txt"
    outside.write_text("secret", encoding="utf-8")
    link = allowed_root / "escape.txt"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("Symlink creation is unavailable")
    with pytest.raises(PermissionError):
        filesystem.read_file(str(link))


def test_output_is_truncated_to_limit(allowed_root: Path) -> None:
    target = allowed_root / "large.txt"
    target.write_text("x" * 50_000, encoding="utf-8")
    assert len(filesystem.read_file(str(target))) == filesystem.MAX_READ_CHARS


def test_health_endpoint() -> None:
    client = TestClient(backend_real.app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["mode"] == "tool-loop"


def test_execution_log_is_written_as_unverified(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(backend_real, "TRACE_DIR", tmp_path / "traces")
    log_path = backend_real.write_execution_log("hello", [{"tool": "read_file", "status": "ok"}], "answer")
    assert log_path is not None
    record = json.loads(Path(log_path).read_text(encoding="utf-8"))
    assert record["kind"] == "execution_log_unverified"
    assert record["query"] == "hello"
    assert record["result"] == "answer"
