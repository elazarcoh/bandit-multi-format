import io
import os
from pathlib import Path

import pytest

import bandit_multi_format


class DummyFileObj:
    def __init__(self, name=None):
        self.name = name


def test_get_formats_env_set_and_parsed(monkeypatch):
    monkeypatch.setenv("BANDIT_MULTI_FORMATS", "json, txt, multi")
    formats = bandit_multi_format._get_formats()
    assert formats == ["json", "txt", "multi"]


def test_get_formats_env_missing_raises(monkeypatch):
    monkeypatch.delenv("BANDIT_MULTI_FORMATS", raising=False)
    with pytest.raises(ValueError):
        bandit_multi_format._get_formats()


def test_get_output_path_prefers_env(monkeypatch, tmp_path):
    monkeypatch.setenv("BANDIT_MULTI_OUTPUT_DIR", str(tmp_path))
    fileobj = DummyFileObj(name=str(tmp_path / "unused.out"))
    out = bandit_multi_format._get_output_path(fileobj)
    assert Path(out) == tmp_path


def test_get_output_path_from_fileobj_when_no_env(monkeypatch, tmp_path):
    monkeypatch.delenv("BANDIT_MULTI_OUTPUT_DIR", raising=False)
    parent = tmp_path / "reports"
    parent.mkdir()
    file_path = parent / "report.out"
    fileobj = DummyFileObj(name=str(file_path))
    out = bandit_multi_format._get_output_path(fileobj)
    assert out == parent


def test_formatter_writes_all_requested_formats(monkeypatch, tmp_path):
    # Arrange: request two fake formats and ensure _get_formatter returns a writer
    monkeypatch.setenv("BANDIT_MULTI_FORMATS", "foo,bar")

    def fake_get_formatter(fmt):
        def writer(manager, out_file, sev_level, conf_level, lines):
            out_file.write(f"written-{fmt}\n")

        return writer

    monkeypatch.setattr(bandit_multi_format, "_get_formatter", fake_get_formatter)

    # Use a fileobj with a name so the formatter will infer output dir
    out_dir = tmp_path / "outdir"
    out_dir.mkdir()
    fileobj = DummyFileObj(name=str(out_dir / "bandit_report.out"))

    # Act
    bandit_multi_format.formatter(None, fileobj, "HIGH", "MEDIUM", -1)

    # Assert both files were created with expected contents
    f1 = out_dir / "bandit_output.foo"
    f2 = out_dir / "bandit_output.bar"
    assert f1.exists()
    assert f2.exists()
    assert f1.read_text().strip() == "written-foo"
    assert f2.read_text().strip() == "written-bar"
